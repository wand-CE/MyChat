from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('<str:room_name>/', views.RoomView.as_view(), name='room'),
]
