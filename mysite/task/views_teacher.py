"""
Teacher-only views.
All views are protected by @teacher_required.
"""
from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, F

from .models import (
    UserProfile, Topic, Task,
    Submission,
)
from .forms import (
    CreateStudentForm, TopicForm, TaskForm,
)


# ── DECORATOR ────────────────────────────────────────────────────────────────

def teacher_required(view_func):
    """Redirect to login if user is not authenticated or not a teacher."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@teacher_required
def teacher_dashboard(request):
    # Пробуем Window functions (Django 2.0+, любая современная БД)
    try:
        from django.db.models import Window
        from django.db.models.functions import DenseRank

        students = list(
            UserProfile.objects.filter(is_staff=False)
            .annotate(
                rank=Window(
                    expression=DenseRank(),
                    order_by=[F('rating').desc(), F('date_registered').asc()]
                )
            )
            .order_by('-rating', 'date_registered')
        )
    except Exception:
        # Fallback: вычисляем DENSE RANK в Python (без N+1 запросов)
        raw = list(
            UserProfile.objects.filter(is_staff=False)
            .order_by('-rating', 'date_registered')
        )
        current_rank = 0
        prev_rating = object()  # sentinel — не совпадёт ни с каким rating
        counter = 0
        for s in raw:
            counter += 1
            if s.rating != prev_rating:
                current_rank = counter
                prev_rating = s.rating
            s.rank = current_rank
        students = raw

    topics        = Topic.objects.prefetch_related('tasks').all()
    pending_subs  = Submission.objects.filter(status='pending').select_related('user', 'task', 'task__topic')
    recent_subs   = Submission.objects.select_related('user', 'task', 'task__topic').order_by('-created_at')[:15]
    accepted_count = Submission.objects.filter(status='accepted').count()

    return render(request, 'task/teacher/teacher_dashboard.html', {
        'students':       students,
        'topics':         topics,
        'pending_subs':   pending_subs,
        'recent_subs':    recent_subs,
        'total_students': len(students),
        'total_tasks':    Task.objects.count(),
        'pending_count':  pending_subs.count(),
        'accepted_count': accepted_count,
    })


# ── STUDENTS ──────────────────────────────────────────────────────────────────

@teacher_required
def create_student(request):
    form = CreateStudentForm(request.POST or None)
    students = UserProfile.objects.filter(is_staff=False).order_by('-date_registered')

    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        user = UserProfile(
            username   = d['username'],
            email      = d.get('email', ''),
            first_name = d.get('first_name', ''),
            last_name  = d.get('last_name', ''),
            is_staff   = False,
        )
        user.set_password(d['password'])
        user.save()
        messages.success(request, f'Ученик «{user.username}» успешно создан!')
        return redirect('create_student')

    return render(request, 'task/teacher/create_student.html', {
        'form': form, 'students': students,
    })


@teacher_required
@require_POST
def delete_student(request, pk):
    student = get_object_or_404(UserProfile, pk=pk, is_staff=False)
    name = student.username
    student.delete()
    messages.success(request, f'Ученик «{name}» удалён.')
    return redirect('create_student')


# ── TOPICS ────────────────────────────────────────────────────────────────────

@teacher_required
def create_topic(request):
    form = TopicForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        topic = form.save()
        messages.success(request, f'Тема «{topic.title}» создана!')
        return redirect('teacher_dashboard')
    topics = Topic.objects.prefetch_related('tasks').all()
    return render(request, 'task/teacher/create_topic.html', {
        'form': form, 'topics': topics,
    })


@teacher_required
def edit_topic(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    form  = TopicForm(request.POST or None, instance=topic)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Тема «{topic.title}» обновлена.')
        return redirect('teacher_dashboard')
    return render(request, 'task/teacher/edit_topic.html', {
        'form': form, 'topic': topic,
    })


@teacher_required
@require_POST
def delete_topic(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    name  = topic.title
    topic.delete()
    messages.success(request, f'Тема «{name}» удалена.')
    return redirect('teacher_dashboard')


# ── TASKS ─────────────────────────────────────────────────────────────────────

@teacher_required
def create_task(request):
    form = TaskForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        task = form.save()
        messages.success(request, f'Задача #{task.number} добавлена!')
        return redirect('teacher_dashboard')
    return render(request, 'task/teacher/create_task.html', {'form': form})


@teacher_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST or None, instance=task)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Задача обновлена.')
        return redirect('teacher_dashboard')
    return render(request, 'task/teacher/edit_task.html', {
        'form': form, 'task': task,
    })


@teacher_required
@require_POST
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    messages.success(request, 'Задача удалена.')
    return redirect('teacher_dashboard')
