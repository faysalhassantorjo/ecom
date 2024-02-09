from django.contrib import admin
from .models import *

# Register your models here.
# admin.site.register(Product)
@admin.register(Product)
class PostAdmin(admin.ModelAdmin):
    class Media:
        js= ('tineyInject.js',)

admin.site.register(UserProfile)
admin.site.register(OrderItem)
admin.site.register(AnonymousUser)
admin.site.register(Order)
admin.site.register(ProductCategory)
admin.site.register(ShippingAddress)
admin.site.register(Review)
admin.site.register(CollectionSet)
admin.site.register(Cuppon)
admin.site.register(AddOnProduct)