from django.urls import path
from . import views

urlpatterns = [
    path('', views.workout_list, name='workout_list'),
    path('add/', views.workout_add, name='workout_add'),
    path('edit/<int:workout_id>/', views.workout_edit, name='workout_edit'),
    path('delete/<int:workout_id>/', views.workout_delete, name='workout_delete'),
]
