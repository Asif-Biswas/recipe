from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from account.models import UserProfile

# Create your models here.
    

class Tag(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    

class Recipe(models.Model):
    subject = models.CharField(max_length=100)
    image = models.ImageField(upload_to='recipe_images', blank=True)
    description = models.TextField(blank=True)
    instructions = RichTextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    liked_by = models.ManyToManyField(User, related_name='liked_recipes', blank=True)
    is_private = models.BooleanField(default=False)
    
    def tags_as_list(self):
        return [tag.name for tag in self.tags.all()]
    
    def __str__(self):
        return self.subject
    
    def user_profile(self):
        return UserProfile.objects.get(user=self.created_by)