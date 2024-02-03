
from django.urls import path,include
from .views import *

urlpatterns = [

    path('', home, name='home'),
    path('update_item/',create_order_item, name="update_item"),
    path('cart/',cart, name="cart"),
    path('myorder/<int:pk>',profile, name="profile"),
    path('checkout/',checkout, name="checkout"),
    path('shop-grid/<int:pk>',shop_grid, name="shop_grid"),
    path('shop-details/<int:pk>',shop_details, name="shop_details"),
    path('write-review/<int:pk>',writeReview, name="writeReview"),
    path('view-order/',viewOrder, name="viewOrder"),
    path('login/',login, name="login"),
    path('logout/',logoutV, name="logout"),
    path('register/',register, name="register"),
    path('order-success/<int:pk>',order_success, name="order_success"),
    path('order-cancel/<int:pk>',order_cancel, name="order_cancel"),
    path('order-status/<int:pk>',order_status, name="order_status"),
    path('products/<int:pk>',products, name="products"),
    path('add-products/',product_add, name="product_add"),
    path('add-category/',addCategory, name="addCategory"),
    path('add-collection/',addCollection, name="addCollection"),
    path('edit-product/<int:pk>/<int:pk2>',edit_product, name="edit_product"),
    path('delete-product/<int:pk>/<int:pk2>',delete_product, name="delete_product"),
    path('confirm-page/<int:pk>/<int:pk2>',confirm_page, name="confirm_page"),


]