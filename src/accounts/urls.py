from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home_page, name='home'),
    path('product/<int:product_id>/', views.product_details, name='product_details'),

    # Cart
    path('cart/', views.shopping_cart, name='shopping_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Authentication
    path('login/', views.login_register, name='login_register'),
    path('login/submit/', views.login_user, name='login_user'),
    path('register/submit/', views.register_user, name='register_user'),
    path('logout/', views.logout_user, name='logout_user'),

    # Buyer Portal
    path('profile/', views.buyer_profile, name='buyer_profile'),
    path('orders/', views.order_history, name='order_history'),

    # Artisan Portal
    path('artisan/dashboard/', views.artisan_dashboard, name='artisan_dashboard'),
    path('artisan/listing/', views.create_edit_listing, name='create_listing'),
    path('artisan/listing/<int:product_id>/', views.create_edit_listing, name='edit_listing'),
    path('artisan/fulfillment/', views.fulfillment_page, name='fulfillment'),
    path('artisan/inventory/', views.inventory_manager, name='inventory_manager'),
    path('artisan/reports/', views.reports_page, name='reports_page'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    # CART ACTION ROUTES
    path('cart/update/<int:item_id>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path("checkout/", views.checkout_page, name="checkout"),
    path('order/place/', views.place_order, name='place_order'),
    path("invoice/", views.invoice_page, name="invoice_page"),

]
