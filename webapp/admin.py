from django.contrib import admin

# Register your models here.
from .models import Stories, Authors
admin.site.register(Stories)
admin.site.register(Authors)
