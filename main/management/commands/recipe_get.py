from django.core.management.base import BaseCommand
from main.models import Recipe
import rich


class Command(BaseCommand):
    help = 'Prints the details of a recipe in markdown format.'

    def add_arguments(self, parser):
        parser.add_argument('recipe_id', type=int)

    def handle(self, *args, **kwargs):
        recipe_id = kwargs['recipe_id']
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            self.stdout.write("Subject: " + recipe.subject)
            tags = recipe.tags_as_list()
            self.stdout.write("Tags: " + ', '.join(tags))
            rich.print(f"[green]Description: {recipe.description}[/green]")
        except Recipe.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Recipe with ID {recipe_id} does not exist."))

