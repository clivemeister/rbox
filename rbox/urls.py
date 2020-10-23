from django.urls import path

from . import views

urlpatterns = [
    # matches /rbox/
    path('', views.index, name='index'),
    # matches /rbox/recipelist/
    path('', views.recipeList, name='recipelist')
    # matches /rbox/5/recipe
    path('<int:recipe_id>/recipe/', views.recipe,name='recipe')
]
