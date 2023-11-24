from django.urls import path
from . import views

urlpatterns = [
    path('', views.ChatView.as_view(), name='home'),
    path('return_chat/', views.ReturnChat.as_view(), name='return_chat'),
    path('search_page', views.SearchView.as_view(), name='search_page'),
    path('chat/get_old_messages/',
         views.GetOldMessages.as_view(), name='old_messages'),
    path('profile/edit/', views.UpdateProfile.as_view(), name='profileSettings'),
    path('create_group/', views.CreateGroup.as_view(), name='createGroup'),
    path('modifyGroup/', views.ModifyGroup.as_view(), name='modifyGroup'),
]
