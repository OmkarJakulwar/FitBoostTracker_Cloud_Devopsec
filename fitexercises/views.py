from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Exercise
from .forms import ExerciseForm
from fitworkouts.models import Workout


@login_required
def exercise_overview(request):
    """Show all exercises across workouts with an optional filter by workout type."""
    workout_type = request.GET.get('type')
    exercises = Exercise.objects.select_related('workout').filter(workout__user=request.user)
    if workout_type:
        exercises = exercises.filter(workout__workout_type=workout_type)

    exercises = exercises.order_by('-workout__workout_date', '-id')
    workout_types = Workout.WORKOUT_TYPES

    return render(request, 'fitexercises/exercise_overview.html', {
        'exercises': exercises,
        'workout_types': workout_types,
        'active_type': workout_type,
    })


@login_required
def exercise_list(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    exercises = workout.exercises.all().order_by('-id')  # newest id will come first
    return render(request, 'fitexercises/exercise_list.html', {'workout': workout, 'exercises': exercises})

@login_required
def exercise_add(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    form = ExerciseForm()
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.workout = workout
            exercise.save()
            messages.success(request, "Exercise added successfully.")
            return redirect('exercise_list', workout_id=workout.id)
    return render(request, 'fitexercises/exercise_add.html', {
        'form': form, 
        'workout': workout
    })

@login_required
def exercise_edit(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, workout__user=request.user)
    form = ExerciseForm(instance=exercise)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            messages.success(request, "Exercise updated successfully.")
            return redirect('exercise_list', workout_id=exercise.workout.id)
    return render(request, 'fitexercises/exercise_edit.html', {
        'form': form, 
        'exercise': exercise
    })

@login_required
def exercise_delete(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, workout__user=request.user)
    workout_id = exercise.workout.id
    if request.method == 'POST':
        exercise.delete()
        messages.success(request, "Exercise deleted successfully.")
    return redirect('exercise_list', workout_id=workout_id)

