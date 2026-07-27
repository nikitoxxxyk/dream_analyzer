from django.test import TestCase
from dream_api.models import Dream

class DreamModelTest(TestCase):
	def setUp(self):
		self.dream = Dream.objects.create(
			user_id="123456789",
			text="Мне снился сон как я успешно прошел собес",
			interpretation='Сон символизирует истинное желание и волю к победе'
		)

	def test_create_dream(self):
		self.assertEqual(self.dream.user_id, '123456789')
		self.assertEqual(self.dream.text, 'Мне снился сон как я успешно прошел собес')
		self.assertEqual(self.dream.interpretation, 'Сон символизирует истинное желание и волю к победе')
		self.assertIsNotNone(self.dream.created_at)

	
			
