from django.contrib import admin
from .models import Tag, Recipe

# Register your models here.
admin.site.register(Tag)
admin.site.register(Recipe)