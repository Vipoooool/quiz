from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
from django.contrib.auth import views, login, logout, authenticate
from django.views import generic, View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import UploadFileForm, SignUpForm, LogInForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
import json
import re


class HomeView(generic.TemplateView):
    template_name = 'index.html'

class UserProfileView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/login/'
    template_name = 'user_profile.html'

class TimeQuizView(generic.DetailView):
    template_name = 'quiz_detail.html'
    model = Quiz

class TimeQuizListView(generic.ListView):
    template_name = 'time_quiz_list.html'
    queryset = Quiz.objects.filter(quiz_type='TQ')
    context_object_name = 'time_quiz_list'

class MarathonQuizView(generic.ListView):
    template_name = 'marathon_quiz.html'
    queryset = Question.objects.filter(quiz=1)
    context_object_name = 'questions'
    paginate_by = 10

class SignupView(generic.CreateView):
    template_name = 'signup.html'
    form_class = SignUpForm
    # extra_context = {'message': 'test context'}
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        full_name = form.cleaned_data['full_name']
        if full_name:
            self.object.first_name = full_name.split()[0]
            self.object.last_name = full_name.split()[-1]
        self.object.save()
        return super().form_valid(form)

class LoginView(views.LoginView):
    template_name = 'login.html'
    form_class = LogInForm

class LogoutView(views.LogoutView):
    next_page = reverse_lazy('login')


class FileFieldFormView(generic.FormView):
    template_name = 'file_upload.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('add_quiz')

    def parse_qa(self, qa_file, quiz):
        qa_content = qa_file.read().decode()
        qas = qa_content.split('QUES')
        for qai in qas[1:]:
            qsn = re.search(r'\d+\.(.*)\n\(a\)', qai, re.DOTALL).group(1).strip()
            ansrs = re.findall(r'\([abcde]\)(.*)', qai)
            corr_ans = re.search('उत्तर.*\(\s*([abcde])\s*\)', qai).group(1)
            qsn_obj, _ = Question.objects.update_or_create(content=qsn, quiz=quiz)
            print("Question => ", qsn_obj)
            corr_anss = list('abcde')
            for ans in ansrs:
                ans = ans.strip()
                if ans == '':
                    continue
                Answer.objects.update_or_create(content=ans, correct = corr_ans == corr_anss.pop(0), question=qsn_obj)

    def form_valid(self, form):
        files = self.request.FILES.getlist('file_field')
        quiz = Quiz.objects.get(id=form.cleaned_data.get('quiz_name'))
        for f in files:
            try:
                self.parse_qa(f, quiz)
            except Exception as err:
                print(err)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(form.errors)
        print(form.cleaned_data)
        return super().form_invalid(form)

def quiz_data_view(request, qid):
    quiz = Quiz.objects.get(id=qid)
    questions = []
    for q in quiz.get_questions():
        answers = []
        for a in q.get_answers():
            answers.append(a.content)
        questions.append({str(q): answers})
    return JsonResponse({
        'data': questions,
        'time': quiz.time,
    })


def save_quiz_view(request, qid):
    questions = []
    data = request.POST
    data_ = dict(data.lists())

    data_.pop('csrfmiddlewaretoken')

    for k in data_.keys():
        # print('key: ', k)
        question = Question.objects.get(content=k)
        questions.append(question)

    user = request.user
    quiz = Quiz.objects.get(id=qid)

    score = 0
    marks = []
    correct_answer = None

    for q in questions:
        a_selected = request.POST.get(q.content)

        if a_selected != "":
            question_answers = Answer.objects.filter(question=q)
            for a in question_answers:
                if a_selected == a.content:
                    if a.correct:
                        score += 1
                        correct_answer = a.content
                else:
                    if a.correct:
                        correct_answer = a.content

            marks.append({str(q): {'correct_answer': correct_answer, 'answered': a_selected}})
        else:
            marks.append({str(q): 'not answered'})
    
    MarksOfUser.objects.create(quiz=quiz, user=user, score=score)
    
    return JsonResponse({'passed': True, 'score': score, 'marks': marks})
        
def check(request):
    data = json.loads(request.body.decode('utf-8'))
    if Answer.objects.filter(question_id=data['question_id'], id=data['answer_id'], correct = True).exists():
        response = {'answer_id': data['answer_id']}
    else:
        answer_id = Answer.objects.get(question_id=data['question_id'], correct = True).id
        response = {'answer_id': answer_id}
    return JsonResponse(response)