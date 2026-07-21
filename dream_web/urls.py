from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('register/', views.register, name='register'),
	path('dashboard/', views.dashboard, name='dashboard'),
	path('dream/<int:dream_id>/', views.dream_detail, name='dream_detail'),
	# Пути для привязки Telegram
	# path('link-telegram/', views.link_telegram, name='link_telegram'),
	# path('unlink-telegram/', views.unlink_telegram, name='unlink_telegram'),
]

