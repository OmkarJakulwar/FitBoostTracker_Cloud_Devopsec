from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from fitworkouts.models import Workout

class WorkoutViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='omi', password='testpass')
        self.client.login(username='omi', password='testpass')
        self.workout = Workout.objects.create(
            user=self.user,
            workout_type='CARDIO',
            title='Morning Run',
            duration=30,
            intensity=3,
            calories_burned=Decimal('250.00'),
            notes='Felt great!',
            workout_date=timezone.now()
        )

    def test_workout_list_view(self):
        response = self.client.get(reverse('workout_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Morning Run')

    def test_workout_add_view_get(self):
        response = self.client.get(reverse('workout_add'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add New Workout')

    def test_workout_add_view_post(self):
        response = self.client.post(reverse('workout_add'), {
            'workout_type': 'YOGA',
            'title': 'Evening Yoga',
            'duration': 45,
            'intensity': 2,
            'calories_burned': '180.00',
            'notes': 'Relaxing session'
        }, follow=True)
        self.assertRedirects(response, reverse('workout_list'))
        self.assertTrue(Workout.objects.filter(title='Evening Yoga').exists())

    def test_workout_edit_view_get(self):
        response = self.client.get(reverse('workout_edit', args=[self.workout.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Workout')

    def test_workout_edit_view_post(self):
        response = self.client.post(reverse('workout_edit', args=[self.workout.id]), {
            'workout_type': 'RUNNING',
            'title': 'Updated Run',
            'duration': 35,
            'intensity': 4,
            'calories_burned': '300.00',
            'notes': 'Pushed harder today'
        }, follow=True)
        self.assertRedirects(response, reverse('workout_list'))
        self.workout.refresh_from_db()
        self.assertEqual(self.workout.title, 'Updated Run')
        self.assertEqual(self.workout.intensity, 4)

    def test_workout_delete_view_post(self):
        response = self.client.post(reverse('workout_delete', args=[self.workout.id]), follow=True)
        self.assertRedirects(response, reverse('workout_list'))
        self.assertFalse(Workout.objects.filter(id=self.workout.id).exists())

    def test_workout_form_validation(self):
        response = self.client.post(reverse('workout_add'), {
            'workout_type': '',  # Missing required field
            'title': '',
            'duration': 0,  # Invalid value
            'intensity': 6,  # Out of range
            'calories_burned': '-10.00',  # Invalid
        })

        form = response.context['form']  # Extract form from response
        self.assertFormError(form, 'workout_type', 'This field is required.')
        self.assertFormError(form, 'title', 'This field is required.')
        self.assertFormError(form, 'duration', 'Ensure this value is greater than or equal to 1.')
        self.assertFormError(form, 'intensity', 'Select a valid choice. 6 is not one of the available choices.')

