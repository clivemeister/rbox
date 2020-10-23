from django.http import HttpResponse

def index(request):
  return HttpResponse('Hello world.  At the index.')

def recipeDetail(request,recipe_id):
    return HttpResponse("You are looking at receipe %s." % recipe_id)

def recipeList(request):
    return HttpResponse("You are looking at a list of the receipes")
    
