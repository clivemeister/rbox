from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404,render
from django.views import generic
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse

from .models import Recipe, IngredientLine, Ingredient, Category

import logging
logger = logging.getLogger(__name__)

def index(request):
  return HttpResponse('Hello world.  At the index.')

def recipeDetail(request,recipe_id):
    recipe = get_object_or_404(Recipe,pk=recipe_id)
    return render(request, 'rbox/recipe.html', {'recipe': recipe})

class recipeListView(generic.ListView):
    model = Recipe
    paginate_by = 100
    calling_url = ''
    template_name = 'rbox/recipelist.html'  # html template to use - default would be recipe_list, I think
    queryset = Recipe.objects.order_by(Lower('name')) # do this to sort in caseless name order
    context_object_name = 'recipes_list'  # name of queryset for use in html template
    searchTerm_name = ""
    searchTerm_ingredient = ""
    searchTerm_taste = ""
    searchTerm_effort = ""
    searchTerm_category = ""
    searchstring = ""    # concatenation of all used search terms

    def get_queryset(self):
        """
        Work through any query terms on the submitted form and return the
        QuerySet of Recipes that results from adding them together.
        """
        # Get the terms from the submitted GET request (in the URL string)
        self.searchTerm_name = self.request.GET.get('search_name',default='')
        self.searchTerm_ingredient = self.request.GET.get('search_ingredient',default='')
        self.searchTerm_taste = self.request.GET.get('search_taste',default='')
        self.searchTerm_effort = self.request.GET.get('search_effort',default='')
        self.searchTerm_category = self.request.GET.get('search_category',default='')
        # Stack all the queries in a Q object, then run to get the subsetted result
        filters = models.Q()
        if self.searchTerm_name!='':
            filters &= models.Q(name__icontains=self.searchTerm_name)
            self.searchstring=self.searchTerm_name
        if self.searchTerm_ingredient !='':
            filters &= models.Q(ingredientline__ingredient__name__icontains=self.searchTerm_ingredient)
            self.searchstring += (" and " if self.searchstring!="" else "")+self.searchTerm_ingredient
        if self.searchTerm_taste !='':
            filters &= models.Q(taste_score__exact=int(self.searchTerm_taste))
            self.searchstring += (" and taste " if self.searchstring!="" else "Taste ")+self.searchTerm_taste
        if self.searchTerm_effort !='':
            filters &= models.Q(effort_score__exact=int(self.searchTerm_effort))
            self.searchstring += (" and effort " if self.searchstring!="" else "Effort ")+self.searchTerm_effort
        if self.searchTerm_category !='':
            filters &= models.Q(categories__tag=self.searchTerm_category)
            self.searchstring += (" and category " if self.searchstring!="" else "Effort ")+self.searchTerm_category
        logging.debug(filters)
        # Return the result of the stacked query against all the Recipe objects
        return self.model.objects.filter(filters).order_by(Lower('name').asc())

    def get_context_data(self, **kwargs):
        """add variables to the context data from the superclass, to make them available in the template"""
        # Call the base implementation first to get a context object
        context = super().get_context_data(**kwargs)
        # Now add in our new bits of context
        context['searchstring']="anything" if self.searchstring=="" else self.searchstring
        context['category_list']=Category.objects.all()
        return context


class RecipeCreate(generic.edit.CreateView):
    model = Recipe
    template_name_suffix = '_create'
    fields = ['name','']


### I think this is now redunant...
#def recipeSearch(request):
#    """
#    Invoked as /recipeSearch URL, by user hitting "Submit" on recipe list.
#    Get the search terms that were submitted, and redirect to recipe list URL to show
#    appropriate subset of the full recipe list (or the full list, if no search terms)
#    """
#    search_title = request.GET['search_title']
#    search_ingredient = request.GET['search_ingredient']
#    if len(search_title)>0:
#        new_url = reverse('rbox:recipe-sublist',args=[search_title])
#    else:
#        # nothing to search for - return full list
#        new_url = reverse('rbox:recipe-list')
#    return HttpResponseRedirect(new_url)
