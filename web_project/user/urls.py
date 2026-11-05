from django.urls import path
from .import views

urlpatterns =[
      path('user_reg/', views.user_reg, name='user_reg'),
      path('user_login/', views.user_login, name='user_login'),

      path('dashboard/', views.user_dashboard, name='user_dashboard'),
      path('logout/', views.user_logout, name='user_logout'),

       # Wishlist pages
    path('wishlist/', views.user_wishlist, name='user_wishlist'),

    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),

    path('product/<int:product_id>/',views.product_details,name='product_details'),

    path('cart/',views.user_cart,name='user_cart'),

    path('cart/add/<int:product_id>/',views.add_to_cart,name='add_to_cart'),

    path('cart/remove/<int:cart_id>/',views.remove_from_cart,name='remove_from_cart'),

    path(
    'remove-from-wishlist/<int:product_id>/',
    views.remove_from_wishlist,
    name='remove_from_wishlist'
),
    path('checkout/', views.checkout, name='checkout'),

    path(
    'order-placed/<int:order_id>/',
    views.order_placed,
    name='order_placed'
),

    path('my-orders/', views.user_orders, name='user_orders'),

    path('order-details/<int:order_id>/', views.order_details, name='order_details'),

    path('cancel-order/<int:order_id>/',views.cancel_order,name='cancel_order'),

    path('profile/', views.user_profile, name='user_profile'),

    
path(
    'add-to-cart/<int:product_id>/',
    views.add_to_cart,
    name='add_to_cart'
),

path('update-cart-quantity/<int:product_id>/',views.update_cart_quantity,name='update_cart_quantity'),



    


    

]
