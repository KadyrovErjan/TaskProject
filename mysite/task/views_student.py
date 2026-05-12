"""
Student-facing views for Interview Preparation section.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import InterviewTopic, InterviewQuestion


@login_required
def interview_list(request):
    """Show all interview topics with question counts and search/filter."""
    q          = request.GET.get('q', '').strip()
    difficulty = request.GET.get('difficulty', '')
    topic_slug = request.GET.get('topic', '')

    questions = InterviewQuestion.objects.select_related('topic').all()

    if q:
        questions = questions.filter(
            Q(question__icontains=q) | Q(answer__icontains=q)
        )
    if difficulty:
        questions = questions.filter(difficulty=difficulty)
    if topic_slug:
        questions = questions.filter(topic__slug=topic_slug)

    topics = InterviewTopic.objects.prefetch_related('questions').all()

    return render(request, 'task/interview/interview_list.html', {
        'topics':     topics,
        'questions':  questions,
        'q':          q,
        'difficulty': difficulty,
        'topic_slug': topic_slug,
        'total':      questions.count(),
    })


@login_required
def interview_topic_detail(request, slug):
    """Show all questions for a specific topic."""
    topic      = get_object_or_404(InterviewTopic, slug=slug)
    difficulty = request.GET.get('difficulty', '')
    q          = request.GET.get('q', '').strip()

    questions = topic.questions.all()
    if difficulty:
        questions = questions.filter(difficulty=difficulty)
    if q:
        questions = questions.filter(
            Q(question__icontains=q) | Q(answer__icontains=q)
        )

    all_topics = InterviewTopic.objects.all()

    return render(request, 'task/interview/topic_detail.html', {
        'topic':      topic,
        'questions':  questions,
        'difficulty': difficulty,
        'q':          q,
        'all_topics': all_topics,
    })
