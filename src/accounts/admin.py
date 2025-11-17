from django.contrib import admin
from .models import UserProfile
from .models import Product, CartItem, UserProfile

admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(UserProfile)
