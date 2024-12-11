from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import TodoItem
from django.contrib.auth.forms import UserCreationForm


def home(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful")
            return redirect('todo_list_view')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('home')
    return render(request, 'todo_list/home.html')


@login_required
def todo_list_view(request):
    if request.method == 'POST':
        if 'delete' in request.POST:
            task_id = request.POST.get('task_id')
            task = get_object_or_404(TodoItem, id=task_id, user=request.user)
            task.delete()
        else:
            text = request.POST.get('text')
            due_date = request.POST.get('due_date')  # Get due_date from the form

            if text:
                TodoItem.objects.create(
                    text=text,
                    user=request.user,
                    due_date=due_date if due_date else None
                )
                return redirect('todo_list_view')

    tasks = TodoItem.objects.filter(user=request.user).order_by('due_date')
    now = timezone.now()

    for task in tasks:
        if task.due_date:
            due_datetime = timezone.make_aware(datetime.combine(task.due_date, datetime.min.time()), timezone.get_current_timezone())
            delta = due_datetime - now
            if delta.total_seconds() > 0:
                task.days_until_due = delta.days
                remaining_seconds = delta.total_seconds() - (task.days_until_due * 86400)
                task.hours_until_due = int(remaining_seconds // 3600)
                remaining_seconds -= task.hours_until_due * 3600
                task.minutes_until_due = int(remaining_seconds // 60)
                task.overdue = False
            else:
                overdue_seconds = abs(delta.total_seconds())
                task.days_overdue = int(overdue_seconds // 86400)
                overdue_seconds -= task.days_overdue * 86400
                task.hours_overdue = int(overdue_seconds // 3600)
                overdue_seconds -= task.hours_overdue * 3600
                task.minutes_overdue = int(overdue_seconds // 60)
                task.overdue = True
        else:
            task.days_until_due = None
            task.hours_until_due = None
            task.minutes_until_due = None
            task.days_overdue = None
            task.hours_overdue = None
            task.minutes_overdue = None
            task.overdue = False

    return render(request, 'todo_list/todo_list.html', {'tasks': tasks, 'now': now})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful")
            return redirect('todo_list_view')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('home')
    return render(request, 'todo_list/login.html')


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')


def register_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Registration successful! Welcome.")
                return redirect('todo_list_view')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, 'todo_list/register.html', {'form': form})