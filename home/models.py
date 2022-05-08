from django.db import models
from .managers import CustomUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    email = models.EmailField(
		_('email address'),
		unique=True
	)

    def __str__(self):
        return self.first_name or self.username
    
    def save(self, *args, **kwargs):
        self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)

class Quiz(models.Model):    
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=500)    
    quiz_type = models.CharField(max_length=10, choices=(("TQ", "Time"), ("MQ", "Marathon")))
    number_of_questions = models.IntegerField(default=1)
    time = models.IntegerField(help_text="Duration of the quiz in seconds", default="1")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    def get_questions(self):
        return self.question_set.all()
    
class Question(models.Model):
    content = models.CharField(max_length=200)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.content
    
    def get_answers(self):
        return self.answer_set.all()
    
    
class Answer(models.Model):
    content = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"question: {self.question.content}, answer: {self.content}, correct: {self.correct}"
    
class MarksOfUser(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField()
    
    def __str__(self):
        return str(self.quiz)

class UserAnswer(models.Model):
    ans = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attempted = models.BooleanField(default=False)
