"""
Venue type mapping — ported from M2 App/backend/routers/utils.py and competitors.py.
Provides display tags and cascade types derived from raw Google Places types arrays.
"""

_TIER_1: list[str] = [
    "restaurant", "bar", "cafe", "night_club", "pub", "bakery",
    "food_court", "lounge_bar", "cocktail_bar", "hookah_bar", "brewpub",
    "brewery", "wine_bar", "coffee_shop", "coffee_roastery", "coffee_stand",
    "tea_house", "tea_store", "dessert_shop", "confectionery",
    "snack_bar", "juice_shop",
]

_TIER_2: list[str] = [
    "fine_dining_restaurant", "fast_food_restaurant", "family_restaurant",
    "buffet_restaurant", "brunch_restaurant", "breakfast_restaurant",
    "diner", "bistro", "gastropub", "bar_and_grill", "sports_bar",
    "dessert_restaurant", "pastry_shop", "cake_shop", "ice_cream_shop",
    "food_delivery", "health_food_store", "catering_service", "cafeteria",
]

_TIER_3: list[str] = [
    "indian_restaurant", "north_indian_restaurant", "south_indian_restaurant",
    "chinese_restaurant", "italian_restaurant", "seafood_restaurant",
    "pizza_restaurant", "mexican_restaurant", "japanese_restaurant",
    "thai_restaurant", "middle_eastern_restaurant", "american_restaurant",
    "asian_restaurant", "vegetarian_restaurant", "vegan_restaurant",
    "hamburger_restaurant", "chicken_restaurant", "chicken_wings_restaurant",
    "kebab_shop", "shawarma_restaurant", "sandwich_shop",
    "european_restaurant", "mediterranean_restaurant", "lebanese_restaurant",
    "turkish_restaurant", "persian_restaurant", "cantonese_restaurant",
    "korean_restaurant", "ramen_restaurant", "sushi_restaurant",
    "french_restaurant", "british_restaurant", "barbecue_restaurant",
    "fusion_restaurant", "asian_fusion_restaurant",
    "dim_sum_restaurant", "chinese_noodle_restaurant", "noodle_shop",
    "dumpling_restaurant", "steak_house", "tapas_restaurant",
    "tex_mex_restaurant", "taco_restaurant", "burrito_restaurant",
    "hot_dog_restaurant", "hot_dog_stand", "fish_and_chips_restaurant",
    "portuguese_restaurant", "burmese_restaurant", "eastern_european_restaurant",
    "afghani_restaurant", "bagel_shop", "deli", "salad_shop",
    "soup_restaurant", "western_restaurant", "irish_pub",
    "german_restaurant", "australian_restaurant", "malaysian_restaurant",
    "latin_american_restaurant", "vietnamese_restaurant", "tibetan_restaurant",
    "brazilian_restaurant", "african_restaurant", "falafel_restaurant",
    "southwestern_us_restaurant",
]

_NON_FOOD_DESCRIPTORS: list[str] = [
    "live_music_venue", "comedy_club", "wedding_venue", "banquet_hall",
    "event_venue", "karaoke", "beer_garden", "coworking_space",
    "performing_arts_theater", "dance_hall", "wellness_center",
    "sports_complex", "indoor_playground", "amusement_park",
    "video_arcade", "bowling_alley", "internet_cafe", "dog_cafe", "cat_cafe",
]

_TYPE_LABELS: dict[str, str] = {
    # Tier 1
    "restaurant":                   "Restaurant",
    "bar":                          "Bar",
    "cafe":                         "Café",
    "night_club":                   "Night Club",
    "pub":                          "Pub",
    "bakery":                       "Bakery",
    "food_court":                   "Food Court",
    "lounge_bar":                   "Lounge Bar",
    "cocktail_bar":                 "Cocktail Bar",
    "hookah_bar":                   "Hookah Bar",
    "brewpub":                      "Brewpub",
    "brewery":                      "Brewery",
    "wine_bar":                     "Wine Bar",
    "coffee_shop":                  "Coffee Shop",
    "coffee_roastery":              "Coffee Roastery",
    "coffee_stand":                 "Coffee Stand",
    "tea_house":                    "Tea House",
    "tea_store":                    "Tea Store",
    "dessert_shop":                 "Dessert Shop",
    "confectionery":                "Confectionery",
    "snack_bar":                    "Snack Bar",
    "juice_shop":                   "Juice Shop",
    # Tier 2
    "fine_dining_restaurant":       "Fine Dining",
    "fast_food_restaurant":         "Fast Food",
    "family_restaurant":            "Family Restaurant",
    "buffet_restaurant":            "Buffet",
    "brunch_restaurant":            "Brunch",
    "breakfast_restaurant":         "Breakfast",
    "diner":                        "Diner",
    "bistro":                       "Bistro",
    "gastropub":                    "Gastropub",
    "bar_and_grill":                "Bar & Grill",
    "sports_bar":                   "Sports Bar",
    "dessert_restaurant":           "Dessert",
    "pastry_shop":                  "Pastry Shop",
    "cake_shop":                    "Cake Shop",
    "ice_cream_shop":               "Ice Cream",
    "food_delivery":                "Delivery",
    "health_food_store":            "Health Food",
    "catering_service":             "Catering",
    "cafeteria":                    "Cafeteria",
    # Tier 3
    "indian_restaurant":            "Indian",
    "north_indian_restaurant":      "North Indian",
    "south_indian_restaurant":      "South Indian",
    "chinese_restaurant":           "Chinese",
    "italian_restaurant":           "Italian",
    "seafood_restaurant":           "Seafood",
    "pizza_restaurant":             "Pizza",
    "mexican_restaurant":           "Mexican",
    "japanese_restaurant":          "Japanese",
    "thai_restaurant":              "Thai",
    "middle_eastern_restaurant":    "Middle Eastern",
    "american_restaurant":          "American",
    "asian_restaurant":             "Asian",
    "vegetarian_restaurant":        "Vegetarian",
    "vegan_restaurant":             "Vegan",
    "hamburger_restaurant":         "Burgers",
    "chicken_restaurant":           "Chicken",
    "chicken_wings_restaurant":     "Wings",
    "kebab_shop":                   "Kebab",
    "shawarma_restaurant":          "Shawarma",
    "sandwich_shop":                "Sandwiches",
    "european_restaurant":          "European",
    "mediterranean_restaurant":     "Mediterranean",
    "lebanese_restaurant":          "Lebanese",
    "turkish_restaurant":           "Turkish",
    "persian_restaurant":           "Persian",
    "cantonese_restaurant":         "Cantonese",
    "korean_restaurant":            "Korean",
    "ramen_restaurant":             "Ramen",
    "sushi_restaurant":             "Sushi",
    "french_restaurant":            "French",
    "british_restaurant":           "British",
    "barbecue_restaurant":          "BBQ",
    "fusion_restaurant":            "Fusion",
    "asian_fusion_restaurant":      "Asian Fusion",
    "dim_sum_restaurant":           "Dim Sum",
    "chinese_noodle_restaurant":    "Chinese Noodles",
    "noodle_shop":                  "Noodles",
    "dumpling_restaurant":          "Dumplings",
    "steak_house":                  "Steakhouse",
    "tapas_restaurant":             "Tapas",
    "tex_mex_restaurant":           "Tex-Mex",
    "taco_restaurant":              "Tacos",
    "burrito_restaurant":           "Burritos",
    "hot_dog_restaurant":           "Hot Dogs",
    "hot_dog_stand":                "Hot Dogs",
    "fish_and_chips_restaurant":    "Fish & Chips",
    "portuguese_restaurant":        "Portuguese",
    "burmese_restaurant":           "Burmese",
    "eastern_european_restaurant":  "Eastern European",
    "afghani_restaurant":           "Afghani",
    "bagel_shop":                   "Bagels",
    "deli":                         "Deli",
    "salad_shop":                   "Salads",
    "soup_restaurant":              "Soups",
    "western_restaurant":           "Western",
    "irish_pub":                    "Irish Pub",
    "german_restaurant":            "German",
    "australian_restaurant":        "Australian",
    "malaysian_restaurant":         "Malaysian",
    "latin_american_restaurant":    "Latin American",
    "vietnamese_restaurant":        "Vietnamese",
    "tibetan_restaurant":           "Tibetan",
    "brazilian_restaurant":         "Brazilian",
    "african_restaurant":           "African",
    "falafel_restaurant":           "Falafel",
    "southwestern_us_restaurant":   "Southwestern",
    # Non-food descriptors
    "live_music_venue":             "Live Music",
    "comedy_club":                  "Comedy Club",
    "wedding_venue":                "Wedding Venue",
    "banquet_hall":                 "Banquet Hall",
    "event_venue":                  "Event Venue",
    "karaoke":                      "Karaoke",
    "beer_garden":                  "Beer Garden",
    "coworking_space":              "Coworking",
    "performing_arts_theater":      "Performing Arts",
    "dance_hall":                   "Dance Hall",
    "wellness_center":              "Wellness",
    "sports_complex":               "Sports Complex",
    "indoor_playground":            "Indoor Play",
    "amusement_park":               "Amusement Park",
    "video_arcade":                 "Arcade",
    "bowling_alley":                "Bowling",
    "internet_cafe":                "Internet Café",
    "dog_cafe":                     "Dog Café",
    "cat_cafe":                     "Cat Café",
}

_GENERIC_TYPES: frozenset[str] = frozenset({
    "food", "point_of_interest", "establishment",
    "store", "premise", "locality", "political",
    "street_address", "geocode",
    "restaurant", "bar", "cafe",
})

# Module-level sets for O(1) membership checks
_FOOD_TYPES_SET: frozenset[str] = frozenset(_TIER_1 + _TIER_2 + _TIER_3)
_NON_FOOD_SET: frozenset[str] = frozenset(_NON_FOOD_DESCRIPTORS)


def map_venue_types(raw_types: list[str]) -> list[str]:
    """
    Returns up to 5 display label strings from a raw Google Places types array.
    Slot 1: primary food identity (food_in_order[0]).
    Slots 2-4: remaining food types in Google's original order.
    Slot 5: first non-food descriptor if any.
    """
    food_in_order = [t for t in raw_types if t in _FOOD_TYPES_SET]
    non_food_in_order = [t for t in raw_types if t in _NON_FOOD_SET]

    selected: list[str] = []
    if food_in_order:
        selected.append(food_in_order[0])
        selected.extend(food_in_order[1:4])  # slots 2-4: up to 3 more food types

    if non_food_in_order:
        selected.append(non_food_in_order[0])  # slot 5

    return [_TYPE_LABELS.get(k, k.replace("_", " ").title()) for k in selected]


def venue_type_cascade(raw_types: list[str]) -> list[str]:
    """
    Returns up to 3 specific (non-generic) types in Google's original order.
    Used for competitor bucket assignment and SE archetype matching.
    """
    result: list[str] = []
    for t in raw_types:
        if t not in _GENERIC_TYPES:
            result.append(t)
            if len(result) == 3:
                break
    return result
