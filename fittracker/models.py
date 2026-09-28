from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    GOAL_CHOICES = [('Lose', 'Lose Weight'), ('Gain', 'Gain Weight'), ('Maintain', 'Maintain Fitness')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(help_text="kg", max_digits=5, decimal_places=2, null=True, blank=True)  # kg
    height = models.DecimalField(help_text="cm", max_digits=5, decimal_places=2, null=True, blank=True)  # cm
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    fitness_goal = models.CharField(max_length=10, choices=GOAL_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_bmi(self):
        if self.height and self.weight:
            return round(self.weight / ((self.height / 100) ** 2), 2)
        return None

    def calculate_bmr(self):
        if self.height and self.weight and self.age and self.gender:
            if self.gender == 'Male':
                return round(10 * self.weight + 6.25 * self.height - 5 * self.age + 5, 2)
            elif self.gender == 'Female':
                return round(10 * self.weight + 6.25 * self.height - 5 * self.age - 161, 2)
        return None

    def __str__(self):
        return f"{self.user.username}'s Profile"
