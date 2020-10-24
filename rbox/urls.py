from django.urls import path

from . import views

urlpatterns = [
    # matches /rbox/
    path('', views.index, name='index'),
    # matches /rbox/recipelist/
    path('recipelist/', views.recipeListView.as_view(), name='recipes'),
    # matches /rbox/recipe/5
    path('recipe/<int:recipe_id>/', views.recipeDetail, name='recipe'),
]
