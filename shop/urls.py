
from django.urls import path,include,re_path
from .views import *


# def handle_unexpected_url(request):
#     return render(request,'shop/404.html')
urlpatterns = [

    path('', home, name='home'),
    path('visit-stats', visit_stats, name='visit_stats'),
    path('update_item/',create_order_item, name="update_item"),
    path('cart/',cart, name="cart"),
    path('location-select/<int:pk>',location_choice, name="location_choice"),
    path('myorder/<int:pk>',profile, name="profile"),
    path('checkout/',checkout, name="checkout"),
    path('shop-grid/<int:pk>',shop_grid, name="shop_grid"),
    path('shop-details/<slug:slug>',shop_details, name="shop_details"),
    path('write-review/<slug:slug>',writeReview, name="writeReview"),
    path('view-order/',viewOrder, name="viewOrder"),
    path('login/',user_login, name="login"),
    path('logout/',logoutV, name="logout"),
    path('register/',register, name="register"),
    path('order-success/<int:pk>',order_success, name="order_success"),
    path('order-cancel/<int:pk>',order_cancel, name="order_cancel"),
    path('order-status/',order_status, name="order_status"),
    path('products/<int:pk>',products, name="products"),
    path('add-products/',product_add, name="product_add"),
    path('add-category/',addCategory, name="addCategory"),
    path('add-collection/',addCollection, name="addCollection"),
    path('edit-product/<int:pk>/<int:pk2>',edit_product, name="edit_product"),
    path('delete-product/<int:pk>/<int:pk2>',delete_product, name="delete_product"),
    path('confirm-page/<int:pk>/<int:pk2>',confirm_page, name="confirm_page"),
     path('go-to-admin/', go_to_admin_panel, name='go_to_admin'),

# re_path(r'^.*$', handle_unexpected_url),
]