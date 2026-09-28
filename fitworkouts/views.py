from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Workout
from .forms import WorkoutForm


@login_required
def workout_list(request):
    workouts = Workout.objects.filter(user=request.user).order_by('-workout_date')
    return render(request, 'workouts/workout_list.html', {
        'workouts': workouts,
    })

@login_required
def workout_add(request):
    form = WorkoutForm()
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            messages.success(request, "Workout added successfully.")
            return redirect('workout_list')
    return render(request, 'workouts/workout_add.html', {'form': form})

@login_required
def workout_edit(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    form = WorkoutForm(instance=workout)
    if request.method == 'POST':
        form = WorkoutForm(request.POST, instance=workout)
        if form.is_valid():
            form.save()
            messages.success(request, "Workout updated successfully.")
            return redirect('workout_list')
    return render(request, 'workouts/workout_edit.html', {'form': form, 'workout': workout})

@login_required
def workout_delete(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        workout.delete()
        messages.success(request, "Workout deleted successfully.")
    return redirect('workout_list')
