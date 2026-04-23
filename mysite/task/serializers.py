from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import (
    UserProfile, Topic, Task, Submission, DailyPlan, LiveLesson,
)

User = get_user_model()


# ─── AUTH ────────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email')
        user = User(username=email, **validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Пользователь с таким email не найден"})
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Неверный пароль"})
        if not user.is_active:
            raise serializers.ValidationError("Пользователь не активен")
        self.context['user'] = user
        return data

    def to_representation(self, instance):
        user = self.context['user']
        refresh = RefreshToken.for_user(user)
        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            RefreshToken(attrs.get('refresh'))
        except Exception:
            raise serializers.ValidationError({"refresh": "Невалидный токен"})
        return attrs


# ─── TEACHER: CREATE STUDENT ──────────────────────────────────────────────────

class CreateStudentSerializer(serializers.ModelSerializer):
    """Учитель создаёт ученика (username + password)."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.is_staff = False  # явно ученик
        if not user.username and user.email:
            user.username = user.email
        user.save()
        return user


# ─── USER ─────────────────────────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'avatar', 'date_registered', 'rating', 'streak', 'is_staff')
        read_only_fields = ('date_registered', 'rating', 'streak', 'is_staff')


# ─── TOPIC & TASK ─────────────────────────────────────────────────────────────

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ('id', 'title', 'description', 'created_at', 'tasks')


class TopicShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'title', 'description', 'created_at')


# ─── SUBMISSION ───────────────────────────────────────────────────────────────

class SubmissionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    task_title = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ('id', 'user', 'user_name', 'task', 'task_title',
                  'code', 'comment', 'status', 'teacher_comment', 'created_at')
        read_only_fields = ('user', 'status', 'teacher_comment', 'created_at')

    def get_task_title(self, obj):
        return f"{obj.task.topic.title} — задача #{obj.task.number}"


class SubmissionReviewSerializer(serializers.ModelSerializer):
    """Только учитель меняет статус и оставляет комментарий."""
    class Meta:
        model = Submission
        fields = ('status', 'teacher_comment')


# ─── DAILY PLAN ───────────────────────────────────────────────────────────────

class DailyPlanSerializer(serializers.ModelSerializer):
    task_info = TaskSerializer(source='task', read_only=True)

    class Meta:
        model = DailyPlan
        fields = ('id', 'user', 'task', 'task_info', 'is_completed')
        read_only_fields = ('user',)


# ─── LIVE LESSON ──────────────────────────────────────────────────────────────

class LiveLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveLesson
        fields = '__all__'
