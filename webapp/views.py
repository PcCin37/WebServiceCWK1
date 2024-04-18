from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Stories, Authors
from datetime import datetime

import json


# Create your views here.
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        # Get the username and password from the request
        username = request.POST['username']
        password = request.POST['password']
        # Check if the author exists
        try:
            author = Authors.objects.get(username=username)
        except Authors.DoesNotExist:
            return HttpResponse('Login failed, no author found.', status=401, content_type='text/plain')

        # Check if the password is correct
        if password == author.password:
            request.session['username'] = username
            return HttpResponse('Hello! Login successful.', status=200, content_type='text/plain')
        else:
            return HttpResponse('Login failed, incorrect password.', status=401, content_type='text/plain')


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        # Check if user is authenticated by checking 'username' in session
        if 'username' in request.session:
            del request.session['username']
            return HttpResponse('Bye! Logout successful.', status=200, content_type='text/plain')
        else:
            return HttpResponse('Logout failed, no login information.', status=400, content_type='text/plain')


class StoryView(View):
    @csrf_exempt
    def get(self, request):
        if request.method == "GET":
            # Get the query parameters
            data = request.GET
            story_cat = data.get('story_cat', None)
            story_region = data.get('story_region', None)
            story_date = data.get('story_date', None)

            # Filter the stories based on the query parameters
            filters = {}
            if story_cat and story_cat != '*':
                filters['category__contains'] = story_cat
            if story_region and story_region != '*':
                filters['region__contains'] = story_region
            if story_date and story_date != '*':
                try:
                    story_date = datetime.strptime(story_date, '%Y-%m-%d').date()
                    filters['date__gte'] = story_date
                except ValueError:
                    return HttpResponse('Invalid date format. Please use YYYY-MM-DD format.', status=400,
                                        content_type='text/plain')

            # Retrieve the stories based on the filters
            stories = Stories.objects.filter(**filters)

            if not stories.exists():
                return HttpResponse('No stories found.', status=404, content_type='text/plain')

            # Prepare the response
            stories_list = [{
                'key': story.id,
                'headline': story.headline,
                'story_cat': story.category,
                'story_region': story.region,
                'author': story.author.realname,
                'story_date': story.date.strftime('%Y-%m-%d'),
                'story_details': story.details
            } for story in stories]

            return JsonResponse({'stories': stories_list}, safe=False, status=200)

    @csrf_exempt
    def post(self, request):
        # Check if user is authenticated by checking 'username' in session
        if 'username' in request.session:
            data = json.loads(request.body)
            username = request.session['username']

            # Check if the author exists
            try:
                author = Authors.objects.get(username=username)
            except Authors.DoesNotExist:
                return HttpResponse('Unauthenticated author.', status=503, content_type='text/plain')

            # Create a new story
            story = Stories(
                headline=data['headline'],
                category=data['category'],
                region=data['region'],
                details=data['details'],
                author=author
            )
            story.save()
            return HttpResponse('Story created successful.', status=201, content_type='text/plain')
        else:
            return HttpResponse('Unauthenticated author.', status=503, content_type='text/plain')


@require_http_methods(["DELETE"])
def delete_story(request, key):
    # Check if user is authenticated by checking 'username' in session
    if 'username' not in request.session:
        return HttpResponse('Authentication required.', status=401, content_type='text/plain')

    # Attempt to retrieve the story with the given key
    try:
        story = Stories.objects.get(pk=key)
    except Stories.DoesNotExist:
        return HttpResponse('No story found.', status=404, content_type='text/plain')

    # Check if the logged-in user is the author of the story
    try:
        username = request.session['username']
        author = Authors.objects.get(username=username)
        if story.author != author:
            return HttpResponse('Unauthorized Access.', status=403,
                                content_type='text/plain')
    except Authors.DoesNotExist:
        return HttpResponse('Unauthenticated author.', status=401, content_type='text/plain')

    # If the user is authorized, delete the story
    story.delete()
    return HttpResponse('Story deleted successfully.', status=200, content_type='text/plain')
