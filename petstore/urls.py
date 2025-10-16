from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Redirect root and /api/ to a useful default endpoint
    path('', RedirectView.as_view(url='/api/pets/', permanent=False)),
    path('api/', RedirectView.as_view(url='/api/pets/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
    path('api/pets/', include('pets.urls')),
    path('api/accessories/', include('accessories.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/addresses/', include('addresses.urls')),
    path('api/carts/', include('carts.urls')),
    path('api/users/', include('users.urls')),
    path('api/contacts/', include('contacts.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
