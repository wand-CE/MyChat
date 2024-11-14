from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.CreateGroup.as_view(), name='createGroup'),
    path('modify/', views.ModifyGroup.as_view(), name='modifyGroup'),
]
