from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


User = get_user_model()

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
                'username': user.username,
                'email': user.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get('refresh')
        try:
            RefreshToken(token)
        except Exception:
            raise serializers.ValidationError({"refresh": "Невалидный токен"})
        return attrs



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'

class DailyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPlan
        fields = '__all__'

class LiveLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveLesson
        fields = '__all__'

class TestSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSession
        fields = '__all__'

class TestParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestParticipant
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class HackathonSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HackathonSession
        fields = '__all__'

class HackathonParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = HackathonParticipant
        fields = '__all__'

class HackathonSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HackathonSubmission
        fields = '__all__'
