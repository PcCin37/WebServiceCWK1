from django.db import models
from django.utils import timezone


# Create your models here.
class Authors(models.Model):
    realname = models.CharField(max_length=20)
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=64)

    def __str__(self):
        return self.realname


class Stories(models.Model):
    CATEGORY_CHOICES = [
        ('pol', 'Politics'),
        ('art', 'Art'),
        ('tech', 'Technology'),
        ('trivia', 'Trivia'),
    ]

    REGION_CHOICES = [
        ('uk', 'UK'),
        ('eu', 'Europe'),
        ('w', 'World'),
    ]

    headline = models.CharField(max_length=64)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    region = models.CharField(max_length=2, choices=REGION_CHOICES)
    author = models.ForeignKey(Authors, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    details = models.CharField(max_length=128)

    def __str__(self):
        return self.headline
