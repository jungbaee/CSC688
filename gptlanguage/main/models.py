from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Question(models.Model):
    question_prompt = models.CharField(max_length=200)
    question = models.CharField(max_length=100, null=True)
    option1 = models.CharField(max_length=100, null=True)
    option2 = models.CharField(max_length=100, null=True)
    option3 = models.CharField(max_length=100, null=True)
    option4 = models.CharField(max_length=100, null=True)
    correct_option = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.question

class QuizResult(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    incorrect_answers = models.PositiveIntegerField(default=0)
    score_percentage = models.DecimalField(default=0.00, max_digits=5,decimal_places=2)
    #timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}  "
    