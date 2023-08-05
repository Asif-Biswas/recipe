from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Recipe, Tag


class Command(BaseCommand):
    help = 'List recipes by tag name'

    def add_arguments(self, parser):
        parser.add_argument('tag_name', type=str, help='The name of the tag to list recipes for')
        parser.add_argument('--number', type=int, default=10, help='The number of recipes to list')

    def handle(self, *args, **options):
        tag_name = options['tag_name']
        recipes = Recipe.objects.filter(tags__name__in=[tag_name])
        recipes = recipes.order_by('-liked_by')[:options['number']]

        for recipe in recipes:
            self.stdout.write(recipe.subject)