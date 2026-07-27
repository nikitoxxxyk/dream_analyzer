from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from dream_api.models import Dream

class WebViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.dream = Dream.objects.create(
            user_id=self.user.id,
            text='Тестовый сон пользователя'
        )

    def test_home_page(self):
        """Тест: главная страница доступна"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        """Тест: дашборд требует авторизации"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Редирект на логин

    def test_dashboard_logged_in(self):
        """Тест: дашборд доступен для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый сон пользователя')
