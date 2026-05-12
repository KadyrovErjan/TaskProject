from django.contrib import admin
from .models import (
    UserProfile, Topic, Task, Submission,
    DailyPlan, LiveLesson,
    InterviewTopic, InterviewQuestion,
)

admin.site.register(UserProfile)
admin.site.register(Topic)
admin.site.register(Task)
admin.site.register(Submission)
admin.site.register(DailyPlan)
admin.site.register(LiveLesson)


@admin.register(InterviewTopic)
class InterviewTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'question_count', 'created_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'topic', 'difficulty', 'created_by', 'created_at')
    list_filter = ('difficulty', 'topic')
    search_fields = ('question', 'answer')
