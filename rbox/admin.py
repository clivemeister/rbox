from django.contrib import admin

# Register your models here.
from .models import Department,Category,Ingredient,IngredientLine,Recipe

admin.site.register(Department)
admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(IngredientLine)
admin.site.register(Recipe)
