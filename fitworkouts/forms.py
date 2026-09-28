from django import forms
from .models import Workout

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['workout_type', 'title', 'duration', 'intensity', 'calories_burned', 'notes']
        widgets = {
            'workout_type': forms.Select(attrs={
                'class': 'form-select'
                }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Morning Run'
                }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '30',
                'min': 1
                }),
            'intensity': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Moderate'
                }),
            'calories_burned': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '250',
                'step': '0.01',
                'min': 0
                }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'How did it feel? Any observations?',
                'rows': 2
                }),
        }
        labels = {
            'workout_type': 'Workout Type',
            'title': 'Title',
            'duration': 'Duration (minutes)',
            'intensity': 'Intensity',
            'calories_burned': 'Calories Burned',
            'notes': 'Notes (Optional)',
        }
        help_texts = {
            'calories_burned': 'Estimated calories burned during workout',
        }
