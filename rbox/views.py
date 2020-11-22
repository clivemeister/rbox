from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404,render,redirect
from django.views import generic
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse, resolve
from django.forms import modelformset_factory,ModelForm,inlineformset_factory
from django.template import loader

from .models import Recipe, IngredientLine, Ingredient, Category
from .forms import IngredientLineForm, RecipeForm, IngredientLineFormSet

import sys
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
        filters = models.Q()
        if 'filter_type' in self.request.GET:
            if self.request.GET['filter_type']=="Clear filter":
                pass # filter is cleared
            elif self.request.GET['filter_type']=="Activate filter":
                # Get the terms from the submitted GET request (in the URL string)
                self.searchTerm_name = self.request.GET.get('search_name',default='')
                self.searchTerm_ingredient = self.request.GET.get('search_ingredient',default='')
                self.searchTerm_taste = self.request.GET.get('search_taste',default='')
                self.searchTerm_effort = self.request.GET.get('search_effort',default='')
                self.searchTerm_category = self.request.GET.get('search_category',default='')
                # Stack all the queries in the Q object, then run to get the subsetted result
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
        context = super().get_context_data(**kwargs)
        context['searchstring']="anything" if self.searchstring=="" else self.searchstring
        context['category_list']=Category.objects.all()
        return context


class recipeCreate(generic.edit.CreateView):
    model = Recipe
    template_name_suffix = '_create'   # With the the default template name is 'recipe_create.html'
    fields = ['name','instructions',
              'taste_score','effort_score','active_minutes','total_minutes',
              'notes','categories','created','source']


def recipe_create(request):
    print("In recipe_create")
    IL_FormSet = inlineformset_factory(Recipe, IngredientLine,
                    form=IngredientLineForm,
                    formset=IngredientLineFormSet,
                    extra=8,
                    can_order=True,
                    can_delete=True,
                 )
    if request.method == 'POST':
        print("POSTed new recipe")
        recipe_form = RecipeForm(request.POST)
        if recipe_form.is_valid():
            recipe = recipe_form.save()
            print(f"saved new recipe <{recipe.name}>")
            ingredients_formset = IL_FormSet(request.POST, instance=recipe)
            if ingredients_formset.is_valid():
                #process recipe.cleaned_data as required
                ingredients_formset.save()
                print(f"saved {ingredients_formset.total_form_count()} ingredient lines")
                target_url = reverse('rbox:recipe-modify', args=(recipe.pk,))
                print("url=",target_url)
                t = loader.get_template('rbox/edit_done.html')
                return HttpResponse(t.render({'url':target_url},request), content_type='text/html')
    else:
        # GETing the recipe_create page, so pass in empty forms
        print("GETting recipe_create page - pass in empty forms",flush=True)
        ingredients_formset = IL_FormSet()
        recipe_form = RecipeForm()

    context = {
        'ingredients_formset': ingredients_formset,
        'recipe' : recipe_form,
    }
    return render(request,'rbox/recipe_create.html', context)


EXTRA_LINES = 3    # add this many extra lines when user clicks "Add more lines" in form
def recipe_modify(request,recipe_id):
    recipe = get_object_or_404(Recipe,pk=recipe_id)
    # Create a class to generate formsets for the ingredientsList
    IL_FormSet = inlineformset_factory(Recipe, IngredientLine,
                    form=IngredientLineForm,
                    formset=IngredientLineFormSet,
                    extra=1,
                    can_order=True,
                    can_delete=True,
                 )
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, instance=recipe) #use existing instance to cause update, not create, on save
        if 'addlines' in request.POST and request.POST['addlines'] == 'true':
            # user has hit "Add more lines"
            formset_dictionary_copy = request.POST.copy()
            current_form_count = int(formset_dictionary_copy['ingredientline_set-TOTAL_FORMS'])
            formset_dictionary_copy['ingredientline_set-TOTAL_FORMS'] = current_form_count + EXTRA_LINES
            ingredients_formset = IL_FormSet(formset_dictionary_copy)
        else:
            # User has hit OK on recipe.  Save the info.
            print("POSTed ingredient list and recipe <%s> after editing"%(recipe.name),flush=True)
            ingredients_formset = IL_FormSet(request.POST, instance=recipe)
            if recipe_form.is_valid() and ingredients_formset.is_valid():
                ingredients_formset.save()
                print("saved ingredient lines")
                recipe_form.save()
                print("Saved the main recipe as well, so acknowledge and redirect")
                target_url = reverse('rbox:recipe-modify', args=(recipe_id,))
                print("url=",target_url)

                t = loader.get_template('rbox/edit_done.html')
                return HttpResponse(t.render({'url':target_url},request), content_type='text/html')
    else:
        # We are loading a recipe & its ingredient lines for modification
        print("GETting ingredient list and recipe <%s> for editing"%(recipe.name),flush=True)
        ingredients_formset = IL_FormSet(instance=recipe)
        recipe_form = RecipeForm(instance=recipe)

    context = {
        'ingredients_formset': ingredients_formset,
        'recipe' : recipe_form,
    }
    return render(request,'rbox/recipe_modify.html', context)

"""
def recipeEdited(request,url):
    return render(request, 'rbox/edit_done.html', {'url': url})


def ingredientList_addform(request):
    ingr_lines = IngredientLine.objects.filter(containing_recipe__name=recipe_name).order_by('line_order')
    IL_FormSet = modelformset_factory(IngredientLine,
                    form=IngredientLineForm,
                    extra=0,
                 )
    formset = IL_FormSet(queryset=ingr_lines)
    # if request.method == "POST":
    #     formset = IL_FormSet(request.POST)
    #     if formset.is_valid():
    #         print("saving valid formset",flush=True)
    #         #save it
    #         pass
    # else:
    #     print("not a POST request to get here",flush=True)
    #     formset = IL_FormSet(queryset = IngredientLine.objects.asc())
    return render(request,'rbox\ingredientlist.html',{'formset': formset})
"""
