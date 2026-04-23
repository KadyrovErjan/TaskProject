"""
Готовый urls.py — замени ПОЛНОСТЬЮ содержимое своего task/urls.py на это.
"""
from django.urls import path
from .views import (
    login_page, logout_page,
    dashboard, tasks_page, task_detail,
    submissions_list, review_submission,
    # DRF API
    RegisterView, CustomLoginView, LogoutView,
    UserProfileListAPIView, UserProfileDetailAPIView,
    TopicListAPIView, TopicDetailAPIView,
    TaskListAPIView, TaskDetailAPIView,
    SubmissionListAPIView, SubmissionDetailAPIView,
    DailyPlanListAPIView, DailyPlanDetailAPIView,
    LiveLessonListAPIView, LiveLessonDetailAPIView,
)
from .views_teacher import (
    teacher_dashboard,
    create_student, delete_student,
    create_topic, edit_topic, delete_topic,
    create_task, edit_task, delete_task,
)

urlpatterns = [

    # ── Auth ──────────────────────────────────────────────────────────────────
    path('login/',  login_page,  name='login'),
    path('logout/', logout_page, name='logout'),

    # ── Student / Shared ──────────────────────────────────────────────────────
    path('',              dashboard,        name='dashboard'),
    path('tasks/',        tasks_page,       name='tasks'),
    path('tasks/<int:pk>/', task_detail,    name='task_detail'),
    path('submissions/',            submissions_list,  name='submissions'),
    path('submissions/<int:pk>/review/', review_submission, name='review_submission'),


    # ── Teacher panel ─────────────────────────────────────────────────────────
    path('teacher/',                              teacher_dashboard, name='teacher_dashboard'),

    # Students
    path('teacher/students/',                     create_student,   name='create_student'),
    path('teacher/students/<int:pk>/delete/',     delete_student,   name='delete_student'),

    # Topics
    path('teacher/topics/create/',                create_topic,     name='create_topic'),
    path('teacher/topics/<int:pk>/edit/',         edit_topic,       name='edit_topic'),
    path('teacher/topics/<int:pk>/delete/',       delete_topic,     name='delete_topic'),

    # Tasks
    path('teacher/tasks/create/',                 create_task,      name='create_task'),
    path('teacher/tasks/<int:pk>/edit/',          edit_task,        name='edit_task'),
    path('teacher/tasks/<int:pk>/delete/',        delete_task,      name='delete_task'),


    # ── DRF API ───────────────────────────────────────────────────────────────
    path('register/',           RegisterView.as_view(),                  name='register'),
    path('api/login/',          CustomLoginView.as_view(),               name='api_login'),
    path('api/logout/',         LogoutView.as_view(),                    name='api_logout'),
    path('user/',               UserProfileListAPIView.as_view(),        name='user_list'),
    path('user/<int:pk>/',      UserProfileDetailAPIView.as_view(),      name='user_detail'),
    path('topic/',              TopicListAPIView.as_view(),              name='topic_list'),
    path('topic/<int:pk>/',     TopicDetailAPIView.as_view(),            name='topic_detail'),
    path('task/',               TaskListAPIView.as_view(),               name='task_list'),
    path('task/<int:pk>/',      TaskDetailAPIView.as_view(),             name='task_detail_api'),
    path('submission/',         SubmissionListAPIView.as_view(),         name='submission_list'),
    path('submission/<int:pk>/', SubmissionDetailAPIView.as_view(),      name='submission_detail'),
    path('dailyplan/',          DailyPlanListAPIView.as_view(),          name='dailyplan_list'),
    path('dailyplan/<int:pk>/', DailyPlanDetailAPIView.as_view(),        name='dailyplan_detail'),
    path('livelesson/',         LiveLessonListAPIView.as_view(),         name='livelesson_list'),
    path('livelesson/<int:pk>/', LiveLessonDetailAPIView.as_view(),      name='livelesson_detail'),
]