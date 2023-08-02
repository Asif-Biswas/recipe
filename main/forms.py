from django import forms
from .models import Recipe
from ckeditor.widgets import CKEditorWidget

class RecipeForm(forms.ModelForm):
    instructions = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Recipe
        fields = ['instructions']