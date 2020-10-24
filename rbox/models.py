from django.db import models

# Create your models here.
class Department(models.Model):
    """
    Departments are locations/aisles in a store where ingredients may be found - fruit, frozen, etc
    """
    dept = models.CharField(max_length=25)

    def __str__(self):
        return self.dept


class Category(models.Model):
    """
    Categories are tags for receipes - vegetarian, lunch, etc.
    There is a many-to-many relationship between Category and Receipe
    """
    tag = models.CharField(max_length=50)

    def __str__(self):
        return self.tag


class Ingredient(models.Model):
    """
    Ingredients are names of constituient food items - onion, tin of sweetcorn, etc
    They have an optional Department where you buy them in a shop
    """
    name = models.CharField(max_length=50)
    dept = models.ForeignKey(Department,
        blank=True,
        default='',
        on_delete=models.SET_DEFAULT
    )

    def __str__(self):
        return self.name


class IngredientLine(models.Model):
    """
    IngredientLines are each found in one Recipis, and each refer to zero or one Ingredients

    """
    line_order = models.SmallIntegerField()
    ingredient = models.ForeignKey('Ingredient',
        default='---',
        null=True,
        on_delete=models.SET_DEFAULT
    )
    containing_recipe = models.ForeignKey('Recipe',
        on_delete=models.CASCADE
    )
    quantity = models.DecimalField(decimal_places=2,max_digits=5,blank=True,default=1)
    quantity_unit = models.CharField(max_length=25,blank=True,default="")
    prep_notes = models.CharField(max_length=200,blank=True)

    def __str__(self):
        return str(self.quantity)+" "+str(self.quantity_unit)+" "+str(self.ingredient)+" "+self.prep_notes


class Recipe(models.Model):
    class TasteRatings(models.IntegerChoices):
        UNRATED = 0
        ONE_STAR = 1
        TWO_STAR = 2
        THREE_STAR = 3
        FOUR_STAR = 4
        FIVE_STAR = 5


    class EffortRatings(models.IntegerChoices):
        UNRATED = 0
        VERY_HARD = 1
        HARD = 2
        MODERATE = 3
        EASY = 4
        VERY_EASY = 5


    name = models.CharField(max_length=100)
    instructions = models.TextField()
    created = models.DateField(blank=True,null=True)
    notes = models.CharField(max_length=200,blank=True,default="")
    taste_score = models.IntegerField(choices=TasteRatings.choices,default=TasteRatings.UNRATED)
    effort_score = models.IntegerField(choices=EffortRatings.choices,default=EffortRatings.UNRATED)
    active_minutes = models.PositiveSmallIntegerField(default=0)
    total_minutes = models.PositiveSmallIntegerField(default=0)
    categories = models.ManyToManyField(Category)
    source = models.CharField(max_length=200,blank=True,default="")

    def taste_stars(self):
        return '*'*self.taste_score if self.taste_score>0 else '-'
    def effort_stars(self):
        return '*'*self.effort_score if self.effort_score>0 else '-'

    def __str__(self):
        return self.name
