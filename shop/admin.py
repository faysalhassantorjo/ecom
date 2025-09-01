from django.contrib import admin
from .models import *
from .form import AddProduct

# Register your models here.
# admin.site.register(Product)
@admin.register(Product)
class PostAdmin(admin.ModelAdmin):
    # form = AddProduct
    # list_display = ("name",)
    # prepopulated_fields = {"slug": ("name",)}
    # exclude =('_ratting',)
    search_fields = ['name', 'slug']
    class Media:
        js= ('tineyInject.js',)

admin.site.register(UserProfile)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(CompletedOrder)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
      list_display = [field.name for field in Order._meta.fields]
      search_fields = ['id', 'user__user__username', 'status','complete']

admin.site.register(ProductCategory)
admin.site.register(ShippingAddress)
admin.site.register(Review)
admin.site.register(CollectionSet)
admin.site.register(Coupon)
# admin.site.register(AddOn)

@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('view_name', 'url','session_address', 'count')
@admin.register(PromoCode)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PromoCode._meta.fields]

admin.site.register(PromoType)
