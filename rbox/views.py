from django.http import HttpResponse
from django.shortcuts import get_object_or_404,render
from .models import Recipe, IngredientLine, Ingredient

def index(request):
  return HttpResponse('Hello world.  At the index.')

def recipeDetail(request,recipe_id):
    recipe = get_object_or_404(Recipe,pk=recipe_id)
    return render(request, 'rbox/recipe.html', {'recipe': recipe})

def recipeList(request):
    return HttpResponse("You are looking at a list of the receipes")
