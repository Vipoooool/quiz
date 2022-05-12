from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
from django.contrib.auth import views, login, logout, authenticate
from django.views import generic, View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import UploadFileForm, SignUpForm, LogInForm
from django.forms import inlineformset_factory
import json

# @login_required(login_url = '/login')
def quiz(request, myid):
    quiz = Quiz.objects.get(id=myid)
    return render(request, "quiz.html", {'quiz':quiz})

def quiz_data_view(request, myid):
    quiz = Quiz.objects.get(id=myid)
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


def save_quiz_view(request, myid):
    if request.is_ajax():
        questions = []
        data = request.POST
        data_ = dict(data.lists())

        data_.pop('csrfmiddlewaretoken')

        for k in data_.keys():
            print('key: ', k)
            question = Question.objects.get(content=k)
            questions.append(question)

        user = request.user
        quiz = Quiz.objects.get(id=myid)

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
        

class HomeView(generic.TemplateView):
    template_name = 'index.html'

class UserProfileView(generic.TemplateView):
    template_name = 'user_profile.html'

class TimeQuizView(generic.TemplateView):
    template_name = 'quiz_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = Quiz.objects.get(id=1)
        return context

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
    success_url = reverse_lazy('index')

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
    form_class = UploadFileForm
    template_name = 'file_upload.html'  # Replace with your template.
    success_url = reverse_lazy('add_quiz')  # Replace with your URL or reverse().

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            quiz = Quiz.objects.get(name=form.cleaned_data.get('quiz_name'))
            for f in files:
                try:
                    parse_qa(f)
                except Exception as err:
                    print(err)
                def parse_qa(file):
                    with open(file) as qa_file:
                        qa_content = qa_file.read()
                    qas = qa_content.split('QUES')
                    for qa in qas[1:]:
                        qa = qa.split('\n')
                        # print(qa)
                        qsn = qa[0]
                        ansrs = qa[2:6]
                        corr_ans = qa[7].split('-')[-1]
                        qsn_obj, _ = Question.objects.update_or_create(content=qsn, quiz=quiz)
                        for ans in ansrs:
                            Answer.objects.update_or_create(content=ans, correct = corr_ans in ans, question=qsn_obj)
                        # print("\nQuestion:", qsn, "\n\nPossible answers:\n", "\n".join(ansrs), "\n\nCorrect answer: ", corr_ans)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

def check(request):
    data = json.loads(request.body.decode('utf-8'))
    if Answer.objects.filter(question_id=data['question_id'], id=data['answer_id'], correct = True).exists():
        response = {'answer_id': data['answer_id']}
    else:
        answer_id = Answer.objects.get(question_id=data['question_id'], correct = True).id
        response = {'answer_id': answer_id}
    return JsonResponse(response)