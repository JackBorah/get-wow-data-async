"""Contians all urls used in get-wow-data"""
urls = {
        "access_token": "https://{region}.battle.net/oauth/token",
        "connected_realm_index": "https://{region}.api.blizzard.com/data/wow/connected-realm/index",
        "realm": "https://{region}.api.blizzard.com/data/wow/connected-realm/{connected_realm_id}",
        "auction": "https://{region}.api.blizzard.com/data/wow/connected-realm/{connected_realm_id}/auctions",
        "profession_index": "https://{region}.api.blizzard.com/data/wow/profession/index",
        "profession_skill_tier": "https://{region}.api.blizzard.com/data/wow/profession/{profession_id}",
        "profession_tier_detail": "https://{region}.api.blizzard.com/data/wow/profession/{profession_id}/skill-tier/{skill_tier_id}",
        "profession_icon": "https://{region}.api.blizzard.com/data/wow/media/profession/{profession_id}",
        "recipe_detail": "https://{region}.api.blizzard.com/data/wow/recipe/{recipe_id}",
        "repice_icon": "https://{region}.api.blizzard.com/data/wow/media/recipe/{recipe_id}",
        "item_classes": "https://{region}.api.blizzard.com/data/wow/item-class/index",
        "item_subclass": "https://{region}.api.blizzard.com/data/wow/item-class/{item_class_id}",
        "item_set_index": "https://{region}.api.blizzard.com/data/wow/item-set/index?",
        "item_icon": "https://{region}.api.blizzard.com/data/wow/media/item/{item_id}",
        "wow_token": "https://{region}.api.blizzard.com/data/wow/token/index",
        "search_realm": "https://{region}.api.blizzard.com/data/wow/search/connected-realm",
        "search_item": "https://{region}.api.blizzard.com/data/wow/search/item",
        "search_media": "https://{region}.api.blizzard.com/data/wow/search/media",
        "icon_test": "https://render.worldofwarcraft.com/",
        "item_bonuses": 'https://www.raidbots.com/static/data/live/bonuses.json',
    }