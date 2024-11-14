from django.urls import path

from . import views

urlpatterns = [
    path('update/', views.UpdateProfile.as_view(), name='profileSettings'),
]
