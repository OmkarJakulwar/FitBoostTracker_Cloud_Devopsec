from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('fittracker.urls')),
    path('workouts/', include('fitworkouts.urls')),
    path('exercises/', include('fitexercises.urls')),
]
