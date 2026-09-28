from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.utils import timezone
from django.http import JsonResponse

from fittracker.forms import UserProfileForm, AvatarForm, CustomPasswordChangeForm
from fittracker.models import UserProfile
from fitexercises.models import Exercise
from fitworkouts.models import Workout

from datetime import datetime, timedelta

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('account_login')

@login_required
def dashboard_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    today = timezone.localdate()
    start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end = timezone.make_aware(datetime.combine(today, datetime.max.time()))

    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    workouts_today = Workout.objects.filter(user=request.user, workout_date__range=(start, end)).count()
    calories_week = Workout.objects.filter(user=request.user, workout_date__gte=start_of_week).aggregate(total=Sum('calories_burned'))['total'] or 0
    workouts_month = Workout.objects.filter(user=request.user, workout_date__gte=start_of_month).count()
    bmi = profile.calculate_bmi()
    
    dashboard_cards = [
        {"label": "Workouts Today", "value": workouts_today, "icon": "bi-calendar-check", "color": "info"},
        {"label": "Calories Burned (Week)", "value": calories_week, "icon": "bi-fire", "color": "danger"},
        {"label": "Workouts (Month)", "value": workouts_month, "icon": "bi-calendar-range", "color": "success"},
        {"label": "Your BMI", "value": bmi or "--", "icon": "bi-heart-pulse", "color": "warning"},
    ]

    latest_workout = Workout.objects.filter(user=request.user).order_by('-workout_date').first()
    latest_exercise = Exercise.objects.filter(workout__user=request.user).order_by('-id').first()

    return render(request, 'dashboard.html', {
        'profile': profile,
        'dashboard_cards': dashboard_cards,
        'latest_workout': latest_workout,
        'latest_exercise': latest_exercise,
    })
    
@login_required
def profile_view(request):
    user = request.user
    profile = user.userprofile

    # Initialize all forms
    avatar_form = AvatarForm(instance=profile)
    profile_form = UserProfileForm(instance=profile)
    password_form = CustomPasswordChangeForm(user=user)

    # Populate initial values from User model
    profile_form.fields['first_name'].initial = user.first_name
    profile_form.fields['last_name'].initial = user.last_name
    profile_form.fields['email'].initial = user.email

    if request.method == 'POST':
        # Avatar upload / clear avatar
        if 'avatar_submit' in request.POST or 'avatar' in request.FILES or 'avatar-clear' in request.POST:
            avatar_form = AvatarForm(request.POST, request.FILES, instance=profile)
            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request, "Avatar updated successfully.")
            return redirect('profile')

        # Profile update
        elif 'profile_submit' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():
                user.first_name = profile_form.cleaned_data.get('first_name', '')
                user.last_name = profile_form.cleaned_data.get('last_name', '')
                user.email = profile_form.cleaned_data.get('email', '')
                user.save()
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
            return redirect('profile')

        # Password change
        elif 'password_submit' in request.POST:
            password_form = CustomPasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Password changed successfully.")
            return redirect('profile')

    return render(request, 'profile.html', {
        'avatar_form': avatar_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'profile': profile,
    })
    
@login_required
def chart_data(request):
    today = timezone.localdate()
    start_of_week = today - timedelta(days=today.weekday())

    # Weekly workout duration
    weekly_data = Workout.objects.filter(user=request.user, workout_date__gte=start_of_week)
    duration_by_day = {day: 0 for day in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']}
    for workout in weekly_data:
        day = workout.workout_date.strftime('%a')[:3]
        duration_by_day[day] += workout.duration

    # Daily calories burned
    calories_by_day = {day: 0 for day in duration_by_day}
    for workout in weekly_data:
        day = workout.workout_date.strftime('%a')[:3]
        calories_by_day[day] += workout.calories_burned

    # Exercise breakdown by name
    exercise_counts = Exercise.objects.filter(workout__user=request.user).values('name').annotate(total=Count('id'))
    exercise_data = {e['name']: e['total'] for e in exercise_counts}

    return JsonResponse({
        'duration_by_day': duration_by_day,
        'calories_by_day': calories_by_day,
        'exercise_data': exercise_data,
    })