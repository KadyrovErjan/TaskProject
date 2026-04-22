from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(Topic)
admin.site.register(Task)
admin.site.register(Submission)
admin.site.register(DailyPlan)
admin.site.register(LiveLesson)
admin.site.register(TestSession)
admin.site.register(TestParticipant)
admin.site.register(Question)
admin.site.register(AnswerOption)
admin.site.register(Answer)
admin.site.register(HackathonSession)
admin.site.register(HackathonParticipant)
admin.site.register(HackathonSubmission)