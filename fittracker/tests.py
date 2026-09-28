from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

from fittracker.models import UserProfile
from fitworkouts.models import Workout
from fitexercises.models import Exercise

class FittrackerViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='omi', password='testpass')
        self.profile = UserProfile.objects.create(user=self.user, height=Decimal('170.00'), weight=Decimal('70.00'))
        self.client.login(username='omi', password='testpass')

    def test_login_view_redirects_authenticated_user(self):
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_dashboard_view_context_data(self):
        today = timezone.localdate()
        aware_datetime = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        workout = Workout.objects.create(
            user=self.user,
            title='Test Workout',
            duration=30,
            calories_burned=300,
            workout_date=aware_datetime,
        )
        Exercise.objects.create(workout=workout, name='Pushups', reps=10, sets=3)

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('dashboard_cards', response.context)
        self.assertIn('latest_workout', response.context)
        self.assertIn('latest_exercise', response.context)
        self.assertEqual(response.context['latest_workout'], workout)

    def test_profile_view_get(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')

    def test_profile_view_avatar_post(self):
        with open('fittracker/tests/test_profile.jpg', 'rb') as avatar:
            response = self.client.post(reverse('profile'), {
                'avatar_submit': '1',
                'avatar': avatar
            }, follow=True)
        self.assertRedirects(response, reverse('profile'))

    def test_profile_view_avatar_clear(self):
        # First upload an avatar for the user
        with open('fittracker/tests/test_profile.jpg', 'rb') as avatar:
            self.client.post(reverse('profile'), {
                'avatar_submit': '1',
                'avatar': avatar
            }, follow=True)

        self.profile.refresh_from_db()
        self.assertTrue(self.profile.avatar)

        # Now clear the avatar using the clear checkbox
        response = self.client.post(reverse('profile'), {
            'avatar_submit': '1',
            'avatar-clear': 'on',
        }, follow=True)
        self.assertRedirects(response, reverse('profile'))

        self.profile.refresh_from_db()
        self.assertFalse(bool(self.profile.avatar))

    def test_profile_view_profile_post(self):
        response = self.client.post(reverse('profile'), {
            'profile_submit': '1',
            'age': 25,
            'height': '175.00',
            'weight': '72.00',
            'gender': 'M',  
            'fitness_goal': 'Gain', 
        }, follow=True)

        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.height, Decimal('175.00'))
        self.assertEqual(updated_profile.weight, Decimal('72.00'))
        self.assertEqual(updated_profile.age, 25)
        self.assertEqual(updated_profile.gender, 'M')
        self.assertEqual(updated_profile.fitness_goal, 'Gain')
        self.assertRedirects(response, reverse('profile'))


    def test_profile_view_password_post(self):
        response = self.client.post(reverse('profile'), {
            'password_submit': '1',
            'old_password': 'testpass',
            'new_password1': 'newsecurepass123',
            'new_password2': 'newsecurepass123'
        }, follow=True)
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newsecurepass123'))

    def test_chart_data_json_response(self):
        today = timezone.localdate()
        aware_datetime = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        workout = Workout.objects.create(
            user=self.user,
            title='Test Workout',
            duration=45,
            calories_burned=400,
            workout_date=aware_datetime,
        )
        Exercise.objects.create(workout=workout, name='Squats', reps=15, sets=4)

        response = self.client.get(reverse('chart_data'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('duration_by_day', data)
        self.assertIn('calories_by_day', data)
        self.assertIn('exercise_data', data)
        self.assertEqual(data['exercise_data']['Squats'], 1)
