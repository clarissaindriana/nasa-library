from django.urls import path

from main.views import show_mainpage

urlpatterns = [
    path('', show_mainpage, name='show_mainpage'),
]