from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404,render
from django.views import generic
from django.db.models.functions import Lower
from django.urls import reverse

from .models import Recipe, IngredientLine, Ingredient

def index(request):
  return HttpResponse('Hello world.  At the index.')

def recipeDetail(request,recipe_id):
    recipe = get_object_or_404(Recipe,pk=recipe_id)
    return render(request, 'rbox/recipe.html', {'recipe': recipe})

class recipeListView(generic.ListView):
    model = Recipe
    paginate_by = 100
    calling_url = ''
    search_term = 'anything'
    template_name = 'rbox/recipelist.html'  # html template to use - default would be recipe_list, I think
    queryset = Recipe.objects.order_by(Lower('name')) # do this to sort in caseless name order
    context_object_name = 'recipes_list'  # name of queryset for use in html template

    def setup(self,request,*args,**kwargs):
        self.calling_url = request.path
        last_element = self.calling_url.split('/')[-2]
        if last_element!='recipelist':
            self.search_term = last_element
        return super().setup(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        """add variables to the context data for this generic view subclass"""
        # Call the base implementation first to get a context object
        context = super().get_context_data(**kwargs)
        # Now add in our new bits of context
        context['search_term']=self.search_term
        context['calling_url']=self.calling_url
        return context

    def get_queryset(self):
        if self.search_term!='anything':
            query_set = self.model.objects.filter(name__icontains=self.search_term)
        else:
            query_set = self.model.objects.all()
        return query_set

def recipeSearch(request):
    search_string = request.GET['search_string']
    new_url = reverse('rbox:recipe-sublist',args=[search_string])
    return HttpResponseRedirect(new_url)
