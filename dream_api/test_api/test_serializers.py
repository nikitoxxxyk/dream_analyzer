from django.test import TestCase
from dream_api.models import Dream
from dream_api.serializers import DreamSerializer

class DreamSerializerTest(TestCase):
	def setUp(self):
		self.dream_data = {
			'user_id': "123456789",
			'text': 'Тестовый сон',
			'interpretation': 'Тестовая интерпретация',
		}
		self.dream = Dream.objects.create(**self.dream_data)

	def test_serializer_fields(self):
		""" Тест на правильное содержание полей """
		serializer = DreamSerializer(self.dream)
		data = serializer.data

		self.assertIn('id', data)
		self.assertIn('user_id', data)
		self.assertIn('text', data)
		self.assertIn('created_at', data)
		self.assertIn('interpretation', data)

	def test_serializer_create(self):
		serializer = DreamSerializer(data={
			'user_id': '111111111',
			'text': 'New dream',
		})

		self.assertTrue(serializer.is_valid())
		dream = serializer.save()
		self.assertEqual(dream.user_id, '111111111')
