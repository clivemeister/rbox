from django.test import TestCase, Client

from .models import Recipe, IngredientLine, Ingredient, Category, Department

import sys
import logging
logger = logging.getLogger(__name__)

# Create your tests here.
class QueryTestCase(TestCase):
    def setUp(self):
        dept_1 = Department.objects.create(dept='chilled')
        dept_2 = Department.objects.create(dept='fruit/veg')

        cat_1 = Category.objects.create(tag='veggie')
        cat_2 = Category.objects.create(tag='lunch')

        ing_1 = Ingredient.objects.create(name='ingredient 1',dept=dept_1)
        ing_2 = Ingredient.objects.create(name='ingredient 2',dept=dept_1)
        ing_3 = Ingredient.objects.create(name='ingredient 3',dept=dept_2)
        ing_4 = Ingredient.objects.create(name='ingredient 4',dept=dept_2)

        self.r_1=Recipe.objects.create(name='lemon meringue pie',
            instructions='instructions 1',
            taste_score=4,
            effort_score=4,
            source="Source One"
        )
        self.ingLine_1_3 = IngredientLine.objects.create(line_order=3,ingredient=ing_3,
                                                        quantity=750,quantity_unit="grams",
                                                        containing_recipe=self.r_1)
        self.ingLine_1_1 = IngredientLine.objects.create(line_order=1,ingredient=ing_1,containing_recipe=self.r_1)
        self.ingLine_1_2 = IngredientLine.objects.create(line_order=2,ingredient=ing_2,
                                                                quantity=1.5,quantity_unit="kilos",
                                                                containing_recipe=self.r_1)

        r_2=Recipe.objects.create(name='lemon drizzle cake',
            instructions='instructions 2',
            taste_score=3,
            effort_score=3,
            source="Source Two"
        )
        ingLine_2_1 = IngredientLine.objects.create(line_order=1,ingredient=ing_1,containing_recipe=r_2)
        ingLine_2_2 = IngredientLine.objects.create(line_order=2,ingredient=ing_3,containing_recipe=r_2)

        r_3=Recipe.objects.create(name='spag bol',
            instructions='instructions 3',
            taste_score=5,
            effort_score=5,
            source="Source One"
        )
        ingLine_3_1 = IngredientLine.objects.create(line_order=1,ingredient=ing_3,containing_recipe=r_3)
        ingLine_3_2 = IngredientLine.objects.create(line_order=2,ingredient=ing_4,containing_recipe=r_3)


    def test_list_all_recipes_returned_alphabetically(self):
        c = Client()
        response = c.get('/rbox/recipelist/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(3,len(list(response.context['recipes_list']))) # check the count
        recip_list = response.context['recipes_list']
        r0 = list(recip_list)[0]
        self.assertEqual(r0.name,'lemon drizzle cake')  # this should be first alphabetically, although added 2nd

    def test_search_of_recipes_redirects(self):
        c = Client()
        response = c.get('/rbox/recipelist?search_name=lemon')  # by default, don't follow redirect
        self.assertRedirects(response,"/rbox/recipelist/?search_name=lemon",status_code=301,target_status_code=200)

    def test_search_recipes_by_part_of_name(self):
        c = Client()
        response = c.get('/rbox/recipelist?search_name=lemon',follow=True)  #follow redirect to get results page
        self.assertEqual(response.status_code,200)
        recip_list = response.context['recipes_list']
        #sys.stderr.write(str(recip_list))
        r_lst = list(recip_list)
        self.assertEqual(2,len(r_lst))  # expecting two recipes in search results
        self.assertEqual(r_lst[0].name,'lemon drizzle cake')  # this should be first
        self.assertEqual(r_lst[1].name,'lemon meringue pie')  # this should be second

    def test_search_recipes_by_part_of_name_and_effort(self):
        c = Client()
        response = c.get('/rbox/recipelist?search_name=lemon&search_taste=4',follow=True)  #follow redirect to get results page
        self.assertEqual(response.status_code,200)
        recip_list = response.context['recipes_list']
        r_lst = list(recip_list)
        self.assertEqual(1,len(r_lst))
        self.assertEqual(r_lst[0].name,'lemon meringue pie')  # this should be only recipe

    def test_get_ingredientslist_in_order(self):
        il = self.r_1.get_ordered_ingredients_list()
        self.assertEqual(il[0],'1.00  ingredient 1 ')
        self.assertEqual(il[1],'1.50 kilos ingredient 2 ')
        self.assertEqual(il[2],'750.00 grams ingredient 3 ')
