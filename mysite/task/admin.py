from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(Topic)
admin.site.register(Task)
admin.site.register(Submission)
admin.site.register(DailyPlan)
admin.site.register(LiveLesson)
