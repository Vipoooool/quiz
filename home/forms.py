from django import forms
from .models import Quiz, Question, Answer
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField, AuthenticationForm

User = get_user_model()

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('name', 'desc', 'number_of_questions', 'time')

    
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('content', 'quiz')

class UploadFileForm(forms.Form):
    quizzes = [(str(q.id), q.name) for q in Quiz.objects.all()]
    # quiz_type = forms.ChoiceField(choices=(("TQ", "Time"), ("MQ", "Marathon")))
    quiz_name = forms.ChoiceField(choices = quizzes)
    time = forms.IntegerField(help_text="Time in seconds if Time Quiz")
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
        
class SignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''
            field.label = False
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Re-enter the password'


    class Meta:
        model = User
        fields = ('email', 'full_name', 'password1', 'password2')
        field_classes = {'username': UsernameField}

class LogInForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.label = False
            field.help_text = ''
            field.widget.attrs['placeholder'] = field_name.capitalize()
        self.fields['username'].widget.attrs['placeholder'] = 'Email'
    
    def get_invalid_login_error(self):
        return forms.ValidationError('Invalid username or password.')