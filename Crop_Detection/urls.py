from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    path('', views.index, name='index'),
    path('result/<int:image_id>/', views.result, name='result'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('feedback/', views.feedback, name='feedback'),
    path('history/', views.history, name='history'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('chatbot/message/', views.chatbot_message, name='chatbot_message'),
    path('chatbot/initialize/', views.chatbot_initialize, name='chatbot_initialize'),
    path('chatbot/clear/', views.chatbot_clear_memory, name='chatbot_clear'),
]

