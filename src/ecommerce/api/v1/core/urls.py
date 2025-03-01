from django.urls import path
from .views import category_list_create, category_detail, product_list_create, product_detail
from .views import cart_list_create, cart_detail, place_order, order_detail, order_list
from .views import track_order_status, update_order_status, list_all_orders, cancel_order
from .views import list_users, block_user, delete_user, product_reviews

urlpatterns = [
    # Categories
    path('categories/', category_list_create, name='category-list-create'),
    path('categories/<int:category_id>/', category_detail, name='category-detail'),

    # Products
    path('products/', product_list_create, name='product-list-create'),
    path('products/<int:product_id>/', product_detail, name='product-detail'),

    # Cart
    path('cart/', cart_list_create, name='cart-list-create'),  # List cart / Add item
    path('cart/<int:cart_id>/', cart_detail, name='cart-detail'),  # Update / Delete item

    #Order
    path('orders/place/', place_order, name='place_order'),
    path('orders/', order_list, name='order_list'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:order_id>/status/', track_order_status, name='track_order_status'),

    #Admin Orders
    path('orders/<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    path('orders/all/', list_all_orders, name='list_all_orders'),
    path('orders/<int:order_id>/cancel/', cancel_order, name='cancel-order'),

    #Admin Users List
    path('users/', list_users, name='list-users'),
    path('users/<int:user_id>/block/', block_user, name='block-user'),
    path('users/<int:user_id>/delete/', delete_user, name='delete-user'),

    #User Reviews
    path('products/<int:product_id>/reviews/', product_reviews, name='product-reviews'),




]