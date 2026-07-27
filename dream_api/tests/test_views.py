from django.test import TestCase
from dream_api.models import Dream
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

class DreamAPITest(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.dream = Dream.objects.create(
			user_id="123456789",
			text='Сон через API клиента',
			interpretation='Интерпретация сна'
		)

	def test_create_dream_success(self):
		url = reverse('create_dream')
		data = {
			'user_id': "987654321",
			'text': 'Новый сон через API клиента'
		}
		response = self.client.post(url, data, format="json")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['user_id'], "987654321")
		self.assertEqual(response.data['text'], 'Новый сон через API клиента')

	def test_create_dream_missing_fields(self):
		url = reverse('create_dream')
		data = {
			'user_id': '123456789'
		}

		response = self.client.post(url, data, format="json")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_get_user_dreams(self):
		"""Тест: получение снов пользователя"""
		url = reverse('user_dreams')
		response = self.client.get(url, {'user_id': '123456789'})
        
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['text'], 'Тестовый сон')		

