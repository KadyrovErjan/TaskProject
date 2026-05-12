"""
Teacher-only views: existing task/topic/student management + new interview prep.
"""
from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import F

from .models import (
    UserProfile, Topic, Task, Submission,
    InterviewTopic, InterviewQuestion,
)
from .forms import (
    CreateStudentForm, TopicForm, TaskForm,
    InterviewTopicForm, InterviewQuestionForm,
)


# ─── DECORATOR ──────────────────────────────────────────────────────────────

def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── RANKING HELPER ─────────────────────────────────────────────────────────

def _ranked_students():
    """Return students queryset annotated with dense rank (Python fallback)."""
    try:
        from django.db.models import Window
        from django.db.models.functions import DenseRank
        return list(
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
        raw = list(
            UserProfile.objects.filter(is_staff=False)
            .order_by('-rating', 'date_registered')
        )
        current_rank = prev_rating = counter = 0
        prev_rating_sentinel = object()
        for s in raw:
            counter += 1
            if s.rating != prev_rating_sentinel:
                prev_rating_val = s.rating
                if counter == 1 or s.rating != prev_rating_sentinel:
                    pass
            # Simple dense rank
        # Redo properly
        current_rank = 0
        prev_val = object()
        for i, s in enumerate(raw):
            if s.rating != prev_val:
                current_rank = i + 1
                prev_val = s.rating
            s.rank = current_rank
        return raw


def _simple_ranked_students():
    raw = list(
        UserProfile.objects.filter(is_staff=False)
        .order_by('-rating', 'date_registered')
    )
    current_rank = 0
    prev_rating = object()  # sentinel
    for i, s in enumerate(raw):
        if s.rating != prev_rating:
            current_rank = i + 1
            prev_rating = s.rating
        s.rank = current_rank
    return raw


# ─── DASHBOARD ──────────────────────────────────────────────────────────────

@teacher_required
def teacher_dashboard(request):
    students = _simple_ranked_students()
    topics        = Topic.objects.prefetch_related('tasks').all()
    pending_subs  = Submission.objects.filter(status='pending').select_related('user', 'task', 'task__topic')
    recent_subs   = Submission.objects.select_related('user', 'task', 'task__topic').order_by('-created_at')[:15]
    accepted_count = Submission.objects.filter(status='accepted').count()

    interview_topic_count    = InterviewTopic.objects.count()
    interview_question_count = InterviewQuestion.objects.count()

    return render(request, 'task/teacher/teacher_dashboard.html', {
        'students':        students,
        'topics':          topics,
        'pending_subs':    pending_subs,
        'recent_subs':     recent_subs,
        'total_students':  len(students),
        'total_tasks':     Task.objects.count(),
        'pending_count':   pending_subs.count(),
        'accepted_count':  accepted_count,
        'interview_topic_count':    interview_topic_count,
        'interview_question_count': interview_question_count,
    })


# ─── STUDENTS ───────────────────────────────────────────────────────────────

@teacher_required
def create_student(request):
    form = CreateStudentForm(request.POST or None)
    students = _simple_ranked_students()

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


# ─── TOPICS ─────────────────────────────────────────────────────────────────

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
    return render(request, 'task/teacher/edit_topic.html', {'form': form, 'topic': topic})


@teacher_required
@require_POST
def delete_topic(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    name  = topic.title
    topic.delete()
    messages.success(request, f'Тема «{name}» удалена.')
    return redirect('teacher_dashboard')


# ─── TASKS ──────────────────────────────────────────────────────────────────

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
    return render(request, 'task/teacher/edit_task.html', {'form': form, 'task': task})


@teacher_required
@require_POST
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    messages.success(request, 'Задача удалена.')
    return redirect('teacher_dashboard')


# ─── INTERVIEW: TEACHER PANEL ────────────────────────────────────────────────

@teacher_required
def interview_dashboard(request):
    """Teacher interview management dashboard."""
    topics    = InterviewTopic.objects.prefetch_related('questions').all()
    questions = InterviewQuestion.objects.select_related('topic').order_by('-created_at')[:20]
    return render(request, 'task/teacher/interview_dashboard.html', {
        'topics':    topics,
        'questions': questions,
        'topic_count':    topics.count(),
        'question_count': InterviewQuestion.objects.count(),
    })


@teacher_required
def interview_topic_create(request):
    form = InterviewTopicForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        topic = form.save()
        messages.success(request, f'Тема «{topic.title}» создана!')
        return redirect('interview_dashboard_teacher')
    topics = InterviewTopic.objects.prefetch_related('questions').all()
    return render(request, 'task/teacher/interview_topic_form.html', {
        'form': form, 'topics': topics, 'action': 'Создать тему',
    })


@teacher_required
def interview_topic_edit(request, pk):
    topic = get_object_or_404(InterviewTopic, pk=pk)
    form  = InterviewTopicForm(request.POST or None, instance=topic)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Тема «{topic.title}» обновлена.')
        return redirect('interview_dashboard_teacher')
    return render(request, 'task/teacher/interview_topic_form.html', {
        'form': form, 'topic': topic, 'action': 'Редактировать тему',
    })


@teacher_required
@require_POST
def interview_topic_delete(request, pk):
    topic = get_object_or_404(InterviewTopic, pk=pk)
    name  = topic.title
    topic.delete()
    messages.success(request, f'Тема «{name}» удалена.')
    return redirect('interview_dashboard_teacher')


@teacher_required
def interview_question_create(request):
    form = InterviewQuestionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        q = form.save(commit=False)
        q.created_by = request.user
        q.save()
        messages.success(request, 'Вопрос добавлен!')
        return redirect('interview_dashboard_teacher')
    return render(request, 'task/teacher/interview_question_form.html', {
        'form': form, 'action': 'Создать вопрос',
    })


@teacher_required
def interview_question_edit(request, pk):
    question = get_object_or_404(InterviewQuestion, pk=pk)
    form     = InterviewQuestionForm(request.POST or None, instance=question)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Вопрос обновлён.')
        return redirect('interview_dashboard_teacher')
    return render(request, 'task/teacher/interview_question_form.html', {
        'form': form, 'question': question, 'action': 'Редактировать вопрос',
    })


@teacher_required
@require_POST
def interview_question_delete(request, pk):
    question = get_object_or_404(InterviewQuestion, pk=pk)
    question.delete()
    messages.success(request, 'Вопрос удалён.')
    return redirect('interview_dashboard_teacher')
