from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.authtoken.views import obtain_auth_token  # Для авторизации через UI DRF

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/tables/', include('tables.urls')),
    
    # Фвторизация через DRF UI
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT Login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
