from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


# =========================
# USER
# =========================
class UserProfile(AbstractUser):
    avatar = models.ImageField(upload_to='profile_img/', null=True, blank=True)
    date_registered = models.DateField(auto_now_add=True)
    rating = models.PositiveIntegerField(default=0)
    streak = models.PositiveIntegerField(default=0)
    last_solved_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username

    def update_streak(self):
        """Call this after an accepted submission is saved."""
        today = timezone.localdate()
        if self.last_solved_date == today:
            # Already counted today
            return
        if self.last_solved_date == today - timezone.timedelta(days=1):
            self.streak += 1
        else:
            self.streak = 1
        self.last_solved_date = today
        self.save(update_fields=['streak', 'last_solved_date'])


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
# SUBMISSION
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
# INTERVIEW PREPARATION
# =========================
class InterviewTopic(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while InterviewTopic.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def question_count(self):
        return self.questions.count()


class InterviewQuestion(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    topic = models.ForeignKey(InterviewTopic, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    answer = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    created_by = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_questions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['difficulty', 'created_at']

    def __str__(self):
        return f"[{self.get_difficulty_display()}] {self.question[:60]}"
