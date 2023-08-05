
from django.core.management.base import BaseCommand
from main.models import Recipe
from rich import print
import os


class Command(BaseCommand):
    help = 'Creates a markdown file with the recipe details.'

    def add_arguments(self, parser):
        parser.add_argument('recipe_id', type=int)

    def handle(self, *args, **kwargs):
        recipe_id = kwargs['recipe_id']
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            filename = f"{recipe.subject}.md"
            with open(filename, 'w') as f:
                f.write(f"# {recipe.subject}\n")
                tags = recipe.tags_as_list()
                f.write('\n'.join([f"- {tag}" for tag in tags]))
                f.write('\n')
                f.write(recipe.description)
            self.stdout.write(self.style.SUCCESS(f"Markdown file '{filename}' created."))
        except Recipe.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Recipe with ID {recipe_id} does not exist."))
