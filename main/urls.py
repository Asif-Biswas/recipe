from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('details/<int:id>/', views.details, name='details'),
    path('create', views.create, name='create'),
    path('tags', views.tags, name='tags'),
    path('tags/<str:tag>', views.tagsearch, name='tags'),
    path('chefs', views.chefs, name='chefs'),
]
