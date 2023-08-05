from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RecipeForm
from .models import Tag, Recipe, UserProfile
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q

# Create your views here.

def home(request):
    recipes = Recipe.objects.filter(is_private=False).order_by('?')[:20]
    return render(request, 'main/home.html', {'recipes': recipes})


def details(request, id):
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
    # order by liked_by count
    recipes = Recipe.objects.filter(tags=tag_ob, is_private=False).order_by('-liked_by')

    return render(request, 'main/tagsearch.html', {'recipes' : recipes, 'tag':tag})


def all_recipes(request):
    recipes = Recipe.objects.filter(is_private=False).order_by('-liked_by')[:100]
    tag = 'All Recipes'
    return render(request, 'main/tagsearch.html', {'recipes' : recipes, 'tag':tag})


def like(request, id):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to login to like a recipe')
        return redirect('account:login')
    recipe = get_object_or_404(Recipe, id=id)
    if request.user in recipe.liked_by.all():
        recipe.liked_by.remove(request.user)
    else:
        recipe.liked_by.add(request.user)
    return redirect('main:details', id=id)


def search(request):
    query = request.GET.get('query')
    recipes = Recipe.objects.filter(Q(subject__icontains=query) | Q(description__icontains=query) | Q(tags__name__icontains=query), is_private=False).distinct().order_by('-liked_by')
    return render(request, 'main/tagsearch.html', {'recipes': recipes, 'tag': query})