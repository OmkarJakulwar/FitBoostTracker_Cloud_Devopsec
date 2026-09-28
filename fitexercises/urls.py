from django.urls import path
from . import views

urlpatterns = [
    path('', views.exercise_overview, name='exercise_overview'),
    path('<int:workout_id>/', views.exercise_list, name='exercise_list'),
    path('<int:workout_id>/add/', views.exercise_add, name='exercise_add'),
    path('edit/<int:exercise_id>/', views.exercise_edit, name='exercise_edit'),
    path('delete/<int:exercise_id>/', views.exercise_delete, name='exercise_delete'),
]
