from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    path('', views.index, name='index'),
    path('result/<int:image_id>/', views.result, name='result'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
