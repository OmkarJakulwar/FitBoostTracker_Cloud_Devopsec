from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Workout(models.Model):
    WORKOUT_TYPES = [
        ('CARDIO', 'Cardio'),
        ('STRENGTH', 'Strength Training'),
        ('YOGA', 'Yoga'),
        ('SPORTS', 'Sports'),
        ('WALKING', 'Walking'),
        ('RUNNING', 'Running'),
        ('CYCLING', 'Cycling'),
        ('SWIMMING', 'Swimming'),
        ('OTHER', 'Other'),
    ]

    INTENSITY_CHOICES = [
        (1, 'Very Light'),
        (2, 'Light'),
        (3, 'Moderate'),
        (4, 'Hard'),
        (5, 'Very Hard'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPES)
    title = models.CharField(max_length=200)
    duration = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    intensity = models.IntegerField(choices=INTENSITY_CHOICES, default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    calories_burned = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    workout_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.workout_date.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ['-workout_date']
        indexes = [models.Index(fields=['user', '-workout_date'])]
