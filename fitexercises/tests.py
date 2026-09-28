from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from fitworkouts.models import Workout
from .models import Exercise


class ExerciseViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='omi', password='testpass')
        self.client.login(username='omi', password='testpass')

        # Two workouts with different types so we can test filtering
        self.workout_cardio = Workout.objects.create(
            user=self.user,
            workout_type='CARDIO',
            title='Morning Run',
            duration=30,
            intensity=3,
            calories_burned=Decimal('250.00'),
            workout_date=timezone.now(),
        )
        self.workout_strength = Workout.objects.create(
            user=self.user,
            workout_type='STRENGTH',
            title='Evening Lifting',
            duration=40,
            intensity=4,
            calories_burned=Decimal('350.00'),
            workout_date=timezone.now(),
        )

        self.exercise1 = Exercise.objects.create(
            workout=self.workout_cardio,
            name='Running',
            sets=1,
            reps=0,
            distance=Decimal('5.00'),
        )
        self.exercise2 = Exercise.objects.create(
            workout=self.workout_strength,
            name='Bench Press',
            sets=3,
            reps=10,
            weight=Decimal('60.00'),
        )

    def test_exercise_overview_lists_all_exercises(self):
        response = self.client.get(reverse('exercise_overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Running')
        self.assertContains(response, 'Bench Press')

    def test_exercise_overview_filter_by_workout_type(self):
        # Filter by CARDIO should only show cardio workout exercises
        response = self.client.get(reverse('exercise_overview'), {'type': 'CARDIO'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Running')
        self.assertNotContains(response, 'Bench Press')

    def test_exercise_list_for_specific_workout(self):
        url = reverse('exercise_list', args=[self.workout_strength.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Only the strength workout exercise should be shown here
        self.assertContains(response, 'Bench Press')
        self.assertNotContains(response, 'Running')

    def test_exercise_add_get(self):
        url = reverse('exercise_add', args=[self.workout_cardio.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Exercise')

    def test_exercise_add_post(self):
        url = reverse('exercise_add', args=[self.workout_cardio.id])
        response = self.client.post(url, {
            'name': 'Intervals',
            'sets': 4,
            'reps': 0,
            'distance': '2.50',
            'notes': 'Short sprints',
        }, follow=True)
        self.assertRedirects(response, reverse('exercise_list', args=[self.workout_cardio.id]))
        self.assertTrue(Exercise.objects.filter(name='Intervals', workout=self.workout_cardio).exists())

    def test_exercise_edit_post(self):
        url = reverse('exercise_edit', args=[self.exercise2.id])
        response = self.client.post(url, {
            'name': 'Bench Press',
            'sets': 4,
            'reps': 10,
            'weight': '65.00',
            'notes': 'Heavier set',
        }, follow=True)
        self.assertRedirects(response, reverse('exercise_list', args=[self.workout_strength.id]))
        self.exercise2.refresh_from_db()
        self.assertEqual(self.exercise2.sets, 4)
        self.assertEqual(self.exercise2.weight, Decimal('65.00'))

    def test_exercise_delete_post(self):
        url = reverse('exercise_delete', args=[self.exercise1.id])
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('exercise_list', args=[self.workout_cardio.id]))
        self.assertFalse(Exercise.objects.filter(id=self.exercise1.id).exists())


class ExerciseAuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='omi', password='testpass')
        self.workout = Workout.objects.create(
            user=self.user,
            workout_type='CARDIO',
            title='Protected Run',
            duration=20,
            intensity=3,
            calories_burned=Decimal('150.00'),
            workout_date=timezone.now(),
        )

    def test_exercise_views_require_login(self):
        overview_url = reverse('exercise_overview')
        list_url = reverse('exercise_list', args=[self.workout.id])
        add_url = reverse('exercise_add', args=[self.workout.id])

        for url in [overview_url, list_url, add_url]:
            response = self.client.get(url)
            # login_required should redirect to login page
            self.assertEqual(response.status_code, 302)
            self.assertIn('/accounts/login/', response.url)
