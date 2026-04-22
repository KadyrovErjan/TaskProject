from django.contrib.auth.models import AbstractUser
from django.db import models


# =========================
# USER
# =========================
class UserProfile(AbstractUser):
    avatar = models.ImageField(upload_to='profile_img/', null=True, blank=True)
    date_registered = models.DateField(auto_now_add=True)
    rating = models.PositiveIntegerField(default=0)
    streak = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.username


# =========================
# TOPIC & TASK
# =========================
class Topic(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tasks')
    number = models.PositiveIntegerField()
    text_ru = models.TextField()
    text_kg = models.TextField()

    def __str__(self):
        return f"{self.topic.title} - {self.number}"


# =========================
# SUBMISSION (ручная проверка)
# =========================
class Submission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'На проверке'),
        ('accepted', 'Принято'),
        ('rejected', 'Ошибка'),
    )

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    code = models.TextField()
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    teacher_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.task}"


# =========================
# DAILY PLAN
# =========================
class DailyPlan(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)


# =========================
# LIVE LESSON
# =========================
class LiveLesson(models.Model):
    title = models.CharField(max_length=128)
    link = models.URLField()
    is_active = models.BooleanField(default=False)
    start_time = models.DateTimeField()


# =========================
# TEST (KAHOOT)
# =========================
class TestSession(models.Model):
    title = models.CharField(max_length=64)
    join_code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class TestParticipant(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)


class Question(models.Model):
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    time_limit = models.PositiveIntegerField(help_text="В секундах")


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)


class Answer(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    time_taken = models.FloatField(help_text="В секундах")


# =========================
# HACKATHON
# =========================
class HackathonSession(models.Model):
    title = models.CharField(max_length=64)
    join_code = models.CharField(max_length=10)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class HackathonParticipant(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    hackathon = models.ForeignKey(HackathonSession, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)


class HackathonSubmission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'На проверке'),
        ('accepted', 'Принято'),
        ('rejected', 'Ошибка'),
    )

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    hackathon = models.ForeignKey(HackathonSession, on_delete=models.CASCADE)
    code = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    points = models.PositiveIntegerField(default=0)