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
    class Media:
        js= ('tineyInject.js',)

admin.site.register(UserProfile)
admin.site.register(OrderItem)
admin.site.register(AnonymousUser)
# admin.site.register(Order)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
      list_display = [field.name for field in Order._meta.fields]
admin.site.register(ProductCategory)
admin.site.register(ShippingAddress)
admin.site.register(Review)
admin.site.register(CollectionSet)
admin.site.register(Cuppon)
admin.site.register(AddOnProduct)