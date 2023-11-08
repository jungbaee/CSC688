from django.contrib import admin
from .models import Question, QuizResult

# Register your models here.
admin.site.register(Question)
admin.site.register(QuizResult)