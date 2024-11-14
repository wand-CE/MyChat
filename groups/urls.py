from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.CreateGroup.as_view(), name='createGroup'),
    path('modifyGroup/', views.ModifyGroup.as_view(), name='modifyGroup'),
]
