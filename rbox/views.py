from django.http import HttpResponse
from django.shortcuts import get_object_or_404,render
from django.views import generic
from django.db.models.functions import Lower

from .models import Recipe, IngredientLine, Ingredient

def index(request):
  return HttpResponse('Hello world.  At the index.')

def recipeDetail(request,recipe_id):
    recipe = get_object_or_404(Recipe,pk=recipe_id)
    return render(request, 'rbox/recipe.html', {'recipe': recipe})

class recipeListView(generic.ListView):
    model = Recipe
    paginate_by = 100
    template_name = 'rbox/recipelist.html'  # default would be recipe_list, I think
    queryset = Recipe.objects.order_by(Lower('name')) # do this to sort in caseless name order
