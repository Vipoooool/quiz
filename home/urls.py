from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("time_quiz_list/", views.TimeQuizListView.as_view(), name="time_quiz_list"),
    path("time_quiz/", views.TimeQuizView.as_view(), name="time_quiz"),
    path("marathon_quiz/", views.MarathonQuizView.as_view(), name="marathon_quiz"),
    path("add_quiz/", views.FileFieldFormView.as_view(), name="add_quiz"),
    # path("<int:myid>/", views.QuizView.as_view(), name="quiz_detail"),


    # path("<int:myid>/", views.quiz, name="quiz"), 
    path('<int:myid>/data/', views.quiz_data_view, name='quiz-data'),
    path('<int:myid>/save/', views.save_quiz_view, name='quiz-save'),
    path('check/', views.check, name='quiz-check'),
    
    path("user_profile/", views.UserProfileView.as_view(), name="user_profile"),
    
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),   
]