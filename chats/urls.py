from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('chat/<str:chat_uuid>/', views.ChatView.as_view(), name='chat'),
    path('redirect_to_chat/<str:user1>/<str:user2>', views.RedirectChat.as_view(), name='redirect_chat'),
    path('search_page/', views.SearchView.as_view(), name='search_page'),
    # path('search_result', views.SearchView.results, name='search_results'),
]
