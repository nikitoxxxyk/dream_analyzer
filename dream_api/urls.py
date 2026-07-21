from django.urls import path
from . import views

urlpatterns = [
    path('create-dream/', views.create_dream, name='create_dream'),
	path('user-dreams/', views.user_dreams, name='user_dreams'),
	path('last-dream/', views.last_dream, name='last_dream'),
]
