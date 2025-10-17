from fastmcp import FastMCP
import requests
import re
from typing import List, Dict, Any

MEALDB_BASE = "https://www.themealdb.com/api/json/v1/1"
mcp = FastMCP("MealMCP") # name of the MCP service

def parse_ingredients_from_context(context: str) -> List[str]:
    text = (context or "").lower()
    text = re.sub(r'[^\w\s,]', ' ', text)
    for marker in ["i have", "ingredients:", "i've got", "i got"]:
        if marker in text:
            text = text.split(marker, 1)[1]
            break
    if ',' in text:
        parts = [p.strip() for p in text.split(",") if p.strip()]
    else:
        parts = [p.strip() for p in text.split() if p.strip()]
    ingredients = [p for p in parts if 1 <= len(p) <= 30]
    return ingredients

def meals_by_ingredient(ingredient: str):
    url = f"{MEALDB_BASE}/filter.php?i={ingredient}"
    r = requests.get(url, timeout=6)
    if r.status_code != 200:
        return []
    return r.json().get("meals") or []

def meal_details(meal_id: str):
    url = f"{MEALDB_BASE}/lookup.php?i={meal_id}"
    r = requests.get(url, timeout=6)
    if r.status_code != 200:
        return None
    data = r.json().get("meals")
    return data[0] if data else None

def meal_ingredients(detail_obj: Dict[str, Any]) -> List[Dict[str,str]]:
    ingredients = []
    for i in range(1, 21):
        ing = detail_obj.get(f"strIngredient{i}")
        measure = detail_obj.get(f"strMeasure{i}")
        if ing and ing.strip():
            ingredients.append({"ingredient": ing.strip(), "measure": (measure or "").strip()})
    return ingredients

@mcp.tool()
def suggest_meal(context: str) -> Dict[str, Any]:
    """
    Suggest a meal based on 'context' string containing ingredients.
    Returns a JSON-serializable dict with recipe info.
    """
    if not context or not isinstance(context, str):
        return {"error": "Please provide 'context' containing ingredients (string)."}
    
    ingredients = parse_ingredients_from_context(context)
    if not ingredients:
        return {"error": "Couldn't parse ingredients. Example: 'I have chicken, rice.'"}
    
    primary = ingredients[0]
    candidates = meals_by_ingredient(primary)
    if not candidates:
        return {"message": f"No meals found from '{primary}'."}
    
    requested = set(i.lower() for i in ingredients)

    best = None
    best_score = -1
    for c in candidates[:25]: # limit for speed
        mid = c.get("idMeal")
        details = meal_details(mid)
        if not details:
            continue
        ingr_list = [x["ingredient"].lower() for x in meal_ingredients(details)]
        score = sum(1 for req in requested if any(req in ing for ing in ingr_list))
        if score > best_score:
            best_score = score
            best = (details, ingr_list)
        if best_score == len(requested):
            break
    
    if not best:
        details = meal_details(candidates[0].get("idMeal"))
        if not details:
            return {"error": "Couldn't fetch meail details."}
        best = (details, [x["ingredient"].lower() for x in meal_ingredients(details)])

    details, ingredients_found = best
    response = {
        "recipe": details.get("strMeal"),
        "category": details.get("strCategory"),
        "area": details.get("strArea"),
        "instructions": details.get("strInstructions"),
        "youtube": details.get("strYoutube"),
        "source": details.get("strSource"),
        "matched_requested_ingredients": list(requested.intersection(set(ingredients_found))),
    }
    return response
    
if __name__ == "__main__":
    # Start the FastMCP server (default HTTP transport)
    # mcp.run()
    mcp.run(transport="http", host="127.0.0.1", port=8000)