from django.db import models

# Create your models here.
class Department(models.Model):
    """Departments are locations/aisles in a store where ingredients may be found - fruit/veg, frozen, etc
    """
    dept = models.CharField(max_length=25)

    def __str__(self):
        return self.dept


class Category(models.Model):
    """Categories are tags for receipes - vegetarian, lunch, etc.
    There is a many-to-many relationship between Category and Receipe
    """
    tag = models.CharField(max_length=50)

    def __str__(self):
        return self.tag


class Ingredient(models.Model):
    """Ingredients are names of constituient food items - onion, tin of sweetcorn, etc
    They have an optional Department (where you buy them in a shop)
    """
    name = models.CharField(max_length=50)
    dept = models.ForeignKey(Department,
        blank=True,
        default='',
        on_delete=models.SET_DEFAULT
    )

    def __str__(self):
        return self.name

HYPEN_LINE_ID=10   # this is the ingredient show by default - usually the ingredient '-----'
class IngredientLine(models.Model):
    """IngredientLines are each found in one Recipes, and each refer to zero or one Ingredients
    Each line has an associated Recipe, a line order to show where it appears in that Recipe's ingredient list,
    an Ingredient field (linked to that model), and an optional quantity, unit for that quantity, and prep notes
    """
    line_order = models.SmallIntegerField()
    ingredient = models.ForeignKey('Ingredient',
        default=HYPEN_LINE_ID,
        null=True,
        on_delete=models.SET_DEFAULT
    )
    containing_recipe = models.ForeignKey('Recipe',
        on_delete=models.CASCADE
    )
    quantity = models.DecimalField(decimal_places=2,max_digits=5,blank=True,default=0)
    quantity_unit = models.CharField(max_length=25,blank=True,default="")
    prep_notes = models.CharField(max_length=200,blank=True,default="")

    def __str__(self):
        s = f"{self.line_order}: " + str(self.ingredient)
        s += f" <{self.quantity} {self.quantity_unit}> <{self.prep_notes}>"
        return s

    def save(self, *args, **kwargs):
        print(f"saving line pk={self.pk}: {self}")
        super().save(*args, **kwargs)


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

    name = models.CharField(max_length=100,db_index=True)
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

    def get_ordered_ingredients_list(self):
        """
        Return a list of strings, each of which is one of the IngredientLines for this recipe
        """
        ingredientsList = list()
        for IL in self.ingredientline_set.order_by('line_order').all():
            ingredientsList.append(str(IL))
        return ingredientsList

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recipe has been saved - make sure the ingredientLines list is ordered 1..N
        print("In Recipe Model save - includes updating IngredientLines ")
        i=1
        for IL in self.ingredientline_set.order_by('line_order').all():
            IL.line_order = i
            IL.save()
            i+=1

    def __str__(self):
        return self.name
