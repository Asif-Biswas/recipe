from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RecipeForm
from .models import Tag, Recipe, UserProfile
from django.shortcuts import get_object_or_404

# Create your views here.

def home(request):
    recipes = Recipe.objects.filter(is_private=False)
    return render(request, 'main/home.html', {'recipes': recipes})


def details(request, id):
    # get or 404
    recipe = get_object_or_404(Recipe, id=id)
    return render(request, 'main/details.html', {'recipe': recipe})


@login_required(login_url='account:login')
def create(request):
    form = RecipeForm()
    tags = Tag.objects.all()

    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        instructions = request.POST.get('instructions')
        tags = request.POST.get('tags')
        image = request.FILES.get('image')
        public = request.POST.get('public')
        recipe = Recipe.objects.create(
            subject=subject,
            description=description,
            instructions=instructions,
            image=image if image else None,
            created_by=request.user,
            is_private=False if public == 'on' else True
        )
        if tags:
            tags = tags.split(',')
            for tag in tags:
                tag = tag.strip()
                tag_obj, created = Tag.objects.get_or_create(name=tag)
                recipe.tags.add(tag_obj)
        return redirect('account:profile')

    return render(request, 'main/create.html', {'form': form, 'tags': tags})


def tags(request):
    tagList = Tag.objects.all()

    return render(request, 'main/tags.html', {'tags': tagList})

def chefs(request):
    chefList = UserProfile.objects.all()
    return render(request, 'main/chefs.html', {"chefs" : chefList})
def tagsearch(request, tag):
    tag_ob = Tag.objects.get(name=tag)
    recipes = Recipe.objects.filter(tags=tag_ob)
    return render(request, 'main/tagsearch.html', {'recipes' : recipes, 'tag':tag})