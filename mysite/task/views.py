from .serializers import *
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .filters import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

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
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
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
    # ordering_fields = ['created_date']

class TopicDetailAPIView(generics.RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

class TaskListAPIView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TaskDetailAPIView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

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

class TestSessionListAPIView(generics.ListAPIView):
    queryset = TestSession.objects.all()
    serializer_class = TestSessionSerializer

class TestSessionDetailAPIView(generics.RetrieveAPIView):
    queryset = TestSession.objects.all()
    serializer_class = TestSessionSerializer

class TestParticipantListAPIView(generics.ListAPIView):
    queryset = TestParticipant.objects.all()
    serializer_class = TestParticipantSerializer

class TestParticipantDetailAPIView(generics.RetrieveAPIView):
    queryset = TestParticipant.objects.all()
    serializer_class = TestParticipantSerializer

class QuestionListAPIView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class QuestionDetailAPIView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class AnswerOptionListAPIView(generics.ListAPIView):
    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer

class AnswerOptionDetailAPIView(generics.RetrieveAPIView):
    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer

class AnswerListAPIView(generics.ListAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class AnswerDetailAPIView(generics.RetrieveAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class HackathonSessionListAPIView(generics.ListAPIView):
    queryset = HackathonSession.objects.all()
    serializer_class = HackathonSessionSerializer

class HackathonSessionDetailAPIView(generics.RetrieveAPIView):
    queryset = HackathonSession.objects.all()
    serializer_class = HackathonSessionSerializer

class HackathonParticipantListAPIView(generics.ListAPIView):
    queryset = HackathonParticipant.objects.all()
    serializer_class = HackathonParticipantSerializer

class HackathonParticipantDetailAPIView(generics.RetrieveAPIView):
    queryset = HackathonParticipant.objects.all()
    serializer_class = HackathonParticipantSerializer

class HackathonSubmissionListAPIView(generics.ListAPIView):
    queryset = HackathonSubmission.objects.all()
    serializer_class = HackathonSubmissionSerializer

class HackathonSubmissionDetailAPIView(generics.RetrieveAPIView):
    queryset = HackathonSubmission.objects.all()
    serializer_class = HackathonSubmissionSerializer
