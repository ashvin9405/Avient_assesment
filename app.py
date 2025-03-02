"""
Assumptions :
1. Given recipe can be cooked with the given ingredients or the ingredients having the same similarity index as given ingredient
2. Will choose same ingredient (given in the recipe which satisfies all conditions)  over the the other 
   ingredient  which have same similarity index but cheaper price. This is because choosing same ingredient 
   given in the recipe will make recipe more accurate
3. Choose the ingredient with lowest price if there are multiple ingredients(satisfying all condition and same similarity index as give element) among the matched ones.
"""

import csv
import os


import json
from dotenv import load_dotenv  # If using python-dotenv

load_dotenv()  # Load .env file

# Parse the JSON string into a dictionary
recipe_ingredients_dict = json.loads(os.getenv("SECRET_RECIPE", "{}"))
# recipe_ingredients_dict = os.getenv("SECRET_RECIPE")

def recipe_in_china(recipe_ingredients : dict) -> dict :

    if not recipe_ingredients_dict :
        return {"message" : "Recipe not found"}

    # Read CSV and convert to list of dictionaries
    with open("ingredients_info.csv", mode="r", encoding="utf-8-sig") as file:

        # Reads CSV into a dictionary format
        reader = csv.DictReader(file)
        # Convert to list of dictionaries
        ingredients_data = [row for row in reader]

    # Sort ingredients_data to get ingredients with similar index together
    sorted_ingredients_data = sorted(ingredients_data, key=lambda x: x.get("Similarity Index"))
    possible_ingredients = []
    similarity_index = []

    # material in recipe : its similarity index
    material_sim_index_dict = {
        x.get("Raw Material ID"): x.get("Similarity Index")
        for x in sorted_ingredients_data
        if x.get("Raw Material ID") in recipe_ingredients.keys()
    }

    # collect all the possible ingredients suitable for recipe 
    # (available in china , melting point >= 200 )
    for possible_ingredient in sorted_ingredients_data:

        raw_material_id = possible_ingredient.get("Raw Material ID")
        current_similarity_index = possible_ingredient.get("Similarity Index")
        availability = possible_ingredient.get("Availability in Country")

        if raw_material_id in recipe_ingredients.keys():
            similarity_index.append(current_similarity_index)

        if (current_similarity_index in similarity_index
            and int(possible_ingredient.get("Melting Point")) >= 200):

            if availability == "ALL":
                possible_ingredients.append(possible_ingredient)

            else:

                if "except" in availability and "China" not in availability :

                    possible_ingredients.append(possible_ingredient)

                else:

                    if "Only" in availability and "China" in availability :

                        possible_ingredients.append(possible_ingredient)

    final_ingredients = []

    # get list of all material ids of possible ingredients
    material_ids = list(map(lambda x: x["Raw Material ID"], possible_ingredients))

    # based on assumptions filter out final ingredients
    for ingredient in recipe_ingredients.keys():

        # if material in recipe is in possible ingredient choose it,
        # without looking for for price (better Accuracy preferred over cost)
        if ingredient in material_ids:
            final_ingredient = [
                x for x in possible_ingredients if x.get("Raw Material ID") == ingredient]

            final_ingredient[0][" Price "] = float(
                (final_ingredient[0].get(" Price ").strip()).lstrip("$"))

            final_ingredients.append(final_ingredient[0])

        # if material in recipe not in possible ingredient choose based on similarity index,
        # among ingredients having same similarity index as ingredient choose with lowest cost
        else:
            similarity_index = material_sim_index_dict.get(ingredient)
            final_ingredient = [
                x
                for x in possible_ingredients
                if x.get("Similarity Index") == similarity_index ]

            sorted_final_ingredient = sorted(
                final_ingredient, key=lambda x: float(x.get(" Price ").strip().lstrip("$")))

            final_ingredient[0][" Price "] = float(
                (final_ingredient[0].get(" Price ").strip()).lstrip("$"))

            final_ingredients.append(sorted_final_ingredient[0])

    recipe_cost = sum(item[" Price "] for item in final_ingredients)

    output = {"recipe_ingredients" : final_ingredients, "recipe_cost($)" : recipe_cost}

    return output


if __name__ == "__main__" :
    final_recipe = recipe_in_china(recipe_ingredients_dict)
    print(final_recipe)
