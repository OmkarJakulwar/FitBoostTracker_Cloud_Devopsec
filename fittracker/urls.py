from django import views
from django.urls import path, include
from django.conf.urls.static import static
from fitboostracker import settings
from fittracker.views import chart_data, login_view, profile_view, dashboard_view

urlpatterns = [
    # URLs included in the below third party app of django:
    #   - /accounts/login/ (user login)
    #   - /accounts/logout/ (user logout)
    #   - /accounts/signup/ (new user registration)
    #   - /accounts/password/reset/ (forgot password)
    path('accounts/', include('allauth.urls')),
    path('', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'), 
    path('chart-data/', chart_data, name='chart_data'),
    path('profile/', profile_view, name='profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
