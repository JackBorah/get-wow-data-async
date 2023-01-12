"""Contians all urls used in get-wow-data-async"""

base_url = "https://{region}.api.blizzard.com"

access_token_url = "https://{region}.battle.net/oauth/token"

paths = {
    "connected_realm_index": "data/wow/connected-realm/index",
    "realm": "data/wow/connected-realm/{connected_realm_id}",
    "auction": "data/wow/connected-realm/{connected_realm_id}/auctions",
    "commodities": "data/wow/auctions/commodities",
    "profession_index": "data/wow/profession/index",
    "profession_skill_tier": "data/wow/profession/{profession_id}",
    "profession_tier_detail": "data/wow/profession/{profession_id}/skill-tier/{skill_tier_id}",
    "profession_icon": "data/wow/media/profession/{profession_id}",
    "recipe_detail": "data/wow/recipe/{recipe_id}",
    "repice_icon": "data/wow/media/recipe/{recipe_id}",
    "item_classes": "data/wow/item-class/index",
    "item_subclass": "data/wow/item-class/{item_class_id}",
    "item_set_index": "data/wow/item-set/index?",
    "item_icon": "data/wow/media/item/{item_id}",
    "item": "data/wow/item/{item_id}",
    "wow_token": "data/wow/token/index",
    "search_realm": "data/wow/search/connected-realm",
    "search_item": "data/wow/search/item",
    "search_media": "data/wow/search/media",
    "item_bonuses": "https://www.raidbots.com/static/data/live/bonuses.json",
    "modified_crafting_reagent_slot_type_index": "data/wow/modified-crafting/reagent-slot-type/index"
}

urls_with_static_namespace = [
        "repice_icon",
        "profession_icon",
        "item_icon",
        "profession_index",
        "profession_skill_tier",
        "profession_tier_detail",
        "profession_icon",
        "recipe_detail",
        "repice_icon",
        "item_classes",
        "item_subclass",
        "item_set_index",
        "item_icon",
        "search_item",
        "item",
        "modified_crafting_reagent_slot_type_index"
    ]