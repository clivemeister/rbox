from django.urls import path

from . import views

app_name = 'rbox'
urlpatterns = [
    # matches /rbox/
    path('', views.index, name='index'),
    # matches /rbox/recipelist/
    path('recipelist/', views.recipeListView.as_view(), name='recipe-list'),
    # matches /rbox/recipelist/searchstring/
    path('recipelist/<str:search_string>/', views.recipeListView.as_view(), name='recipe-sublist'),
    # matches /rbox/recipe/5
    path('recipe/<int:recipe_id>/', views.recipeDetail, name='recipe-in-detail'),
    # matches /rbox/recipesearch/
    path('recipesearch', views.recipeListView.as_view(), name='recipe-search')
]
