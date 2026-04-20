from collections import Counter


CATEGORY_MEDIA = {
    "work-tech": {
        "image_url": "https://loremflickr.com/1600/1200/laptop,workspace?lock=201",
        "image_alt": "Minimal work-tech desk setup with a laptop and productivity accessories.",
        "hero_note": "Portable tools and focused desk gear.",
    },
    "home-living": {
        "image_url": "https://loremflickr.com/1600/1200/blanket,home?lock=202",
        "image_alt": "Soft home living scene with layered textiles and calm interior styling.",
        "hero_note": "Soft accents for brighter rooms.",
    },
    "kitchen-dining": {
        "image_url": "https://loremflickr.com/1600/1200/kitchen,coffee?lock=203",
        "image_alt": "Kitchen counter with coffee tools and simple dining accessories.",
        "hero_note": "Everyday prep and slower kitchen rituals.",
    },
    "wellness": {
        "image_url": "https://loremflickr.com/1600/1200/yoga,wellness?lock=204",
        "image_alt": "Wellness scene with yoga accessories and hydration essentials.",
        "hero_note": "Movement, stretching, and daily balance.",
    },
    "travel-everyday": {
        "image_url": "https://loremflickr.com/1600/1200/travel,bag?lock=205",
        "image_alt": "Travel-ready bag with daily carry essentials in a bright setting.",
        "hero_note": "Carry pieces for short trips and daily errands.",
    },
    "beauty-care": {
        "image_url": "https://loremflickr.com/1600/1200/skincare,beauty?lock=206",
        "image_alt": "Beauty and skincare tabletop with compact daily care products.",
        "hero_note": "Compact beauty tools and gentle care sets.",
    },
}


PRODUCT_MEDIA = {
    "novabook-flex-13": {
        "image_url": "https://loremflickr.com/1600/1200/laptop,desk?lock=301",
        "image_alt": "Slim silver laptop opened on a clean desk with soft daylight.",
    },
    "luma-desk-light": {
        "image_url": "https://loremflickr.com/1600/1200/desk,lamp?lock=302",
        "image_alt": "Minimal desk lamp on a modern work surface.",
    },
    "cloudrest-throw": {
        "image_url": "https://loremflickr.com/1600/1200/throw,blanket?lock=303",
        "image_alt": "Soft woven throw blanket folded on a bed.",
    },
    "aromanest-diffuser": {
        "image_url": "https://loremflickr.com/1600/1200/diffuser,ceramic?lock=304",
        "image_alt": "Ceramic aroma diffuser on a small interior shelf.",
    },
    "brewmate-press": {
        "image_url": "https://loremflickr.com/1600/1200/french,press,coffee?lock=305",
        "image_alt": "French press with coffee styling on a bright kitchen counter.",
    },
    "sliceboard-duo": {
        "image_url": "https://loremflickr.com/1600/1200/cutting,board,kitchen?lock=306",
        "image_alt": "Wooden cutting boards in a clean kitchen scene.",
    },
    "corebalance-mat": {
        "image_url": "https://loremflickr.com/1600/1200/yoga,mat,fitness?lock=307",
        "image_alt": "Yoga mat laid out in a bright training corner.",
    },
    "puresip-bottle": {
        "image_url": "https://loremflickr.com/1600/1200/water,bottle?lock=308",
        "image_alt": "Insulated bottle placed on a minimalist desk.",
    },
    "transit-weekender": {
        "image_url": "https://loremflickr.com/1600/1200/weekender,bag,travel?lock=309",
        "image_alt": "Compact weekender travel bag packed for a short trip.",
    },
    "linencarry-tote": {
        "image_url": "https://loremflickr.com/1600/1200/tote,bag?lock=310",
        "image_alt": "Light tote bag hanging in a bright everyday setting.",
    },
    "glowmirror-mini": {
        "image_url": "https://loremflickr.com/1600/1200/makeup,mirror?lock=311",
        "image_alt": "Portable makeup mirror with soft reflected light.",
    },
    "calmskin-set": {
        "image_url": "https://loremflickr.com/1600/1200/skincare,bottles?lock=312",
        "image_alt": "Skincare starter set styled on a clean vanity surface.",
    },
}


PRODUCT_MEDIA_BY_NAME = {}
for slug, media in PRODUCT_MEDIA.items():
    normalized_name = slug.replace("-", " ").strip()
    PRODUCT_MEDIA_BY_NAME[normalized_name] = media | {"slug": slug}


def normalize_name(value):
    return " ".join((value or "").lower().replace("-", " ").split())


def _category_media(category_slug):
    return CATEGORY_MEDIA.get(category_slug or "", {})


def _product_media(product):
    slug = (product.get("slug") or product.get("product_slug") or "").strip()
    if slug in PRODUCT_MEDIA:
        return PRODUCT_MEDIA[slug]

    normalized_name = normalize_name(product.get("name") or product.get("product") or product.get("product_name"))
    if normalized_name in PRODUCT_MEDIA_BY_NAME:
        return PRODUCT_MEDIA_BY_NAME[normalized_name]

    category = product.get("category") or {}
    category_slug = category.get("slug") or product.get("category_slug")
    return _category_media(category_slug)


def enrich_categories(categories, items):
    counts = Counter((item.get("category") or {}).get("slug") for item in items if item.get("category"))
    enriched = []
    for category in categories:
        category_slug = category.get("slug")
        media = _category_media(category_slug)
        enriched.append(
            {
                **category,
                "image_url": media.get("image_url", ""),
                "image_alt": media.get("image_alt", f"{category.get('name', 'Category')} image"),
                "hero_note": media.get("hero_note", "Curated picks with quieter, easier scanning."),
                "product_count": counts.get(category_slug, 0),
            }
        )
    return enriched


def enrich_product(product):
    if product is None:
        return None
    media = _product_media(product)
    category = product.get("category") or {}
    category_media = _category_media(category.get("slug"))
    return {
        **product,
        "image_url": media.get("image_url", category_media.get("image_url", "")),
        "image_alt": media.get("image_alt", product.get("name", "Product image")),
        "category_image_url": category_media.get("image_url", ""),
        "category_hero_note": category_media.get("hero_note", ""),
    }


def enrich_product_listing(payload):
    if not payload:
        return payload
    items = [enrich_product(item) for item in payload.get("items", [])]
    return {
        **payload,
        "items": items,
        "categories": enrich_categories(payload.get("categories", []), items),
    }


def enrich_product_detail_payload(payload):
    if not payload:
        return payload
    product = enrich_product(payload.get("product"))
    related_products = [enrich_product(item) for item in payload.get("related_products", [])]
    return {
        **payload,
        "product": product,
        "related_products": related_products,
    }


def enrich_cart_payload(payload):
    if not payload:
        return payload
    items = []
    for item in payload.get("items", []):
        product = {
            "product_slug": item.get("product_slug"),
            "product": item.get("product"),
            "category_slug": "",
        }
        media = _product_media(product)
        items.append(
            {
                **item,
                "image_url": media.get("image_url", ""),
                "image_alt": media.get("image_alt", item.get("product", "Cart item image")),
                "product_url": f"/products/{item.get('product_slug')}/" if item.get("product_slug") else "",
            }
        )
    return {
        **payload,
        "items": items,
    }


def enrich_order_detail_payload(payload):
    if not payload:
        return payload
    items = []
    for item in payload.get("items", []):
        media = _product_media(
            {
                "product_name": item.get("product_name"),
                "product": item.get("product_name"),
            }
        )
        items.append(
            {
                **item,
                "image_url": media.get("image_url", ""),
                "image_alt": media.get("image_alt", item.get("product_name", "Order item image")),
            }
        )

    primary_item = items[0] if items else None
    return {
        **payload,
        "items": items,
        "primary_item": primary_item,
    }
