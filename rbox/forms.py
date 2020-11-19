from django import forms
from django.forms import ModelForm, TextInput, Textarea, NumberInput, SelectMultiple
from django.forms import BaseInlineFormSet

from .models import IngredientLine, Ingredient, Recipe


class IngredientLineForm(ModelForm):
    """Handle an ingredient line's display, controlling various field sizes and types
    """
    class Meta:
        model = IngredientLine
        fields = ['line_order','ingredient','quantity','quantity_unit','prep_notes']
        # override the widget used to enter quantity, so we can control its size (can't do that with input=number fields)
        widgets = {
            'line_order': NumberInput(attrs={'style':'width: 3em'}),

            'quantity': TextInput(),
            'prep_notes': TextInput(attrs={'size':40}),
        }

    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)
        self.fields['quantity'].widget.attrs.update({'size':6})
        self.fields['quantity_unit'].widget.attrs.update({'size':10})

    def __repr__(self):
        if self['line_order'].value()==None:
            return super.__str__(self)
        s= f"IngredientLine {self['line_order'].value()}: <Ingredient {self['ingredient'].value()}>"
        s +=f" <qty:{self['quantity'].value()} units:{self['quantity_unit'].value()}> <{self['prep_notes'].value()}>"
        return s
"""
   def updateOrder(self,val):
        print(type(self['line_order']))
        print("updating line order from",self['line_order'].value(),"to",val)
        self.line_order=val
        print(" line order is now",self['line_order'].value(),"should be",val)
"""

class IngredientLineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = IngredientLine.objects.filter(containing_recipe__name=self.instance.name).order_by('line_order')
"""
    def clean(self):
        print("in IngredientLineFormSet.clean()")
        print(f"{self.cleaned_data=}")

        #  re-build the line_order into cleaned_data so that they just the values 1..n (for n lines)
        line_forms={}
        for form in self.forms:
            print(f"{form.cleaned_data=}")
            if form.cleaned_data.get('line_order')!=None:
                line_forms[form.cleaned_data.get('line_order')]=form
        i=1
        for line_order_val in sorted(line_forms):
            line_forms[line_order_val].updateOrder(i)
            print(f"{line_forms[line_order_val]=} {i=}")
            i+=1
        return True
"""

class RecipeForm(ModelForm):
    """Form for user to update a recipe.
    Display version has a separate embedded formset to handle the ingredient list
    """
    class Meta:
        model = Recipe
        fields = ['name','instructions','notes','taste_score','effort_score',
                'categories','active_minutes','total_minutes','source']
        widgets = {'instructions': Textarea(attrs={'cols':80, 'rows':15}),
                   'notes': Textarea(attrs={'cols':80, 'rows':2}),
                   'categories': SelectMultiple(attrs={'style':'vertical-align:top', 'size':10}),
                   'active_minutes': TextInput(attrs={'size':5}),
                   'total_minutes': TextInput(attrs={'size':5}),
                   'source': TextInput(attrs={'size':40})
                  }


    def __init__(self, *args, **kwargs):
        self.recipe = kwargs.pop('recipe', None)
        super().__init__(*args, **kwargs)

    def is_valid(self):
        print("Checking RecipeForm is valid")
        self.valid=True
        return True

    def save(self):
        print("In RecipeForm save")
        return super().save(self)
