from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home + all store routes
    path('', include('accounts.urls')),

    # Accounts routes 
]
