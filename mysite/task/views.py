from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# DRF imports (existing API views)
from .serializers import *
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .filters import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .forms import CreateStudentForm


# ─────────────────────────────────────────────
# DECORATORS
# ─────────────────────────────────────────────

def teacher_required(view_func):
    """Only staff (teachers) can access this view."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def student_required(view_func):
    """Only non-staff (students) can access this view."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('teacher_dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ─────────────────────────────────────────────
# AUTH VIEWS (Django session-based)
# ─────────────────────────────────────────────

def login_page(request):
    if request.user.is_authenticated:
        return redirect('teacher_dashboard' if request.user.is_staff else 'dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('teacher_dashboard')
            return redirect('dashboard')
        else:
            error = 'Неверный логин или пароль'

    return render(request, 'task/login.html', {'error': error})


def logout_page(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')


# ─────────────────────────────────────────────
# TEACHER VIEWS
# ─────────────────────────────────────────────

@teacher_required
def teacher_dashboard(request):
    students            = UserProfile.objects.filter(is_staff=False).order_by('-date_registered')
    topics              = Topic.objects.prefetch_related('tasks').all()
    pending_submissions = Submission.objects.filter(status='pending').select_related('user', 'task', 'task__topic').order_by('-created_at')
    recent_submissions  = Submission.objects.select_related('user', 'task', 'task__topic').order_by('-created_at')[:20]
    ctx = {
        'students':            students,
        'topics':              topics,
        'pending_submissions': pending_submissions,
        'recent_submissions':  recent_submissions,
        'total_students':      students.count(),
        'total_tasks':         Task.objects.count(),
        'pending_count':       pending_submissions.count(),
        'accepted_count':      Submission.objects.filter(status='accepted').count(),
    }
    return render(request, 'task/teacher_dashboard.html', ctx)


@teacher_required
def create_student(request):
    """Create a student account. Can be called from teacher_dashboard modal."""
    if request.method == 'POST':
        form = CreateStudentForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            user = UserProfile(
                username=d['username'],
                email=d.get('email', ''),
                first_name=d.get('first_name', ''),
                last_name=d.get('last_name', ''),
                is_staff=False,
            )
            user.set_password(d['password'])
            user.save()
            messages.success(request, f"Ученик «{user.username}» успешно создан!")
            return redirect('teacher_dashboard')
        else:
            # Pass errors back (modal will re-open)
            messages.error(request, ' '.join([e for field in form.errors.values() for e in field]))
            return redirect('teacher_dashboard')
    return redirect('teacher_dashboard')


@teacher_required
def submissions_list(request):
    submissions = Submission.objects.select_related('user', 'task', 'task__topic').order_by('-created_at')
    return render(request, 'task/submissions.html', {'submissions': submissions})


@teacher_required
def review_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        teacher_comment = request.POST.get('teacher_comment', '')
        if new_status in ('accepted', 'rejected'):
            submission.status = new_status
            submission.teacher_comment = teacher_comment
            submission.save()
            if new_status == 'accepted':
                submission.user.rating += 10
                submission.user.save()
    return render(request, 'task/review submission.html', {'submission': submission})


# ─────────────────────────────────────────────
# STUDENT VIEWS
# ─────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user
    if user.is_staff:
        return redirect('teacher_dashboard')

    my_submissions = Submission.objects.filter(user=user).select_related('task', 'task__topic').order_by('-created_at')
    daily_plans = DailyPlan.objects.filter(user=user).select_related('task', 'task__topic')
    live_lessons = LiveLesson.objects.filter(is_active=True)

    solved = my_submissions.filter(status='accepted').count()
    pending = my_submissions.filter(status='pending').count()
    rejected = my_submissions.filter(status='rejected').count()

    ctx = {
        'my_submissions': my_submissions[:10],
        'daily_plans': daily_plans,
        'live_lessons': live_lessons,
        'solved': solved,
        'pending': pending,
        'rejected': rejected,
        'streak': user.streak,
    }
    return render(request, 'task/dashboard.html', ctx)


@login_required
def tasks_page(request):
    topics = Topic.objects.prefetch_related('tasks').all()

    solved_ids = set()
    pending_ids = set()
    rejected_ids = set()

    if not request.user.is_staff:
        # For each task keep only the latest submission status
        from django.db.models import Max
        latest = (
            Submission.objects
            .filter(user=request.user)
            .values('task_id')
            .annotate(last_id=Max('id'))
        )
        last_ids = [row['last_id'] for row in latest]
        for sub in Submission.objects.filter(id__in=last_ids).values('task_id', 'status'):
            if sub['status'] == 'accepted':
                solved_ids.add(sub['task_id'])
            elif sub['status'] == 'rejected':
                rejected_ids.add(sub['task_id'])
            else:
                pending_ids.add(sub['task_id'])

    return render(request, 'task/tasks.html', {
        'topics': topics,
        'solved_ids': solved_ids,
        'pending_ids': pending_ids,
        'rejected_ids': rejected_ids,
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    last_submission = None
    success = error = None

    if not request.user.is_staff:
        last_submission = Submission.objects.filter(
            user=request.user, task=task
        ).order_by('-created_at').first()

        if request.method == 'POST':
            code = request.POST.get('code', '').strip()
            comment = request.POST.get('comment', '')
            if not code:
                error = 'Напишите код перед отправкой'
            else:
                Submission.objects.create(
                    user=request.user,
                    task=task,
                    code=code,
                    comment=comment,
                    status='pending',
                )
                success = True
                last_submission = Submission.objects.filter(
                    user=request.user, task=task
                ).order_by('-created_at').first()

    ctx = {
        'task': task,
        'last_submission': last_submission,
        'success': success,
        'error': error,
    }
    return render(request, 'task/task_detail.html', ctx)


# ─────────────────────────────────────────────
# DRF API VIEWS (keep existing)
# ─────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomLoginView(generics.GenericAPIView):
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'detail': 'Невалидный токен'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileListAPIView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)


class UserProfileDetailAPIView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class TopicListAPIView(generics.ListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TopicFilter
    search_fields = ['title']


class TopicDetailAPIView(generics.RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class TaskListAPIView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDetailAPIView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class SubmissionListAPIView(generics.ListAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer


class SubmissionDetailAPIView(generics.RetrieveAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer


class DailyPlanListAPIView(generics.ListAPIView):
    queryset = DailyPlan.objects.all()
    serializer_class = DailyPlanSerializer


class DailyPlanDetailAPIView(generics.RetrieveAPIView):
    queryset = DailyPlan.objects.all()
    serializer_class = DailyPlanSerializer


class LiveLessonListAPIView(generics.ListAPIView):
    queryset = LiveLesson.objects.all()
    serializer_class = LiveLessonSerializer


class LiveLessonDetailAPIView(generics.RetrieveAPIView):
    queryset = LiveLesson.objects.all()
    serializer_class = LiveLessonSerializer

