
from .models import *

from django.core.cache import cache
cache_time = 0
def home_query():
    # Top-rated products
    top_rated_products = cache.get('top_rated_products')
    if top_rated_products is None:
        top_rated_products = list(
            Product.objects.filter(ratting__gt=2)
            .only('slug', 'ratting', 'name', 'price')[:6]
        )
        cache.set('top_rated_products', top_rated_products, cache_time)

    # Popular categories
    # popular_category = cache.get('popular_category')
    # if popular_category is None:
    #     popular_category = ProductCategory.objects.filter(is_popular=True).only('id', 'name')
    #     cache.set('popular_category', popular_category, cache_time)

    # Hero collections
    hero_collections = cache.get('hero_collections')
    if hero_collections is None:
        hero_collections = CollectionSet.objects.filter(hero=True).only('id').order_by('-id')
        cache.set('hero_collections', hero_collections, cache_time)

    # Non-hero collections
    collection_sets = cache.get('collection_sets')
    if collection_sets is None:
        collection_sets = CollectionSet.objects.filter(hero=False).only('id')
        cache.set('collection_sets', collection_sets, cache_time)

    # Discount products
    # discount_products = cache.get('discount_products')
    # if discount_products is None:
    #     discount_products = list(
    #         Product.objects.filter(discount_percent__gt=5)
    #         .only('slug', 'discount_percent', 'name', 'price')[:8]
    #     )
    #     cache.set('discount_products', discount_products, cache_time)

    # All categories
    all_categories = cache.get('all_categories')
    if all_categories is None:
        all_categories = list(ProductCategory.objects.all().only('id', 'name'))
        cache.set('all_categories', all_categories, 60*60*2)
        print('Category Cached')

    # New arrivals
    # new_arrivals = cache.get('new_arrivals')
    # if new_arrivals is None:
    #     new_arrivals = list(Product.get_new_arrivals()[:8])
    #     cache.set('new_arrivals', new_arrivals, cache_time)

    return {
        'top_rated_product': top_rated_products,
        'heroCollections': hero_collections,
        'collectionsets': collection_sets,
        # 'discount_products': discount_products,
        'all_categories': all_categories,
        # 'new_arrivals': new_arrivals,
        # 'popular_category': popular_category,
    }
