from django.db import models

class Dream(models.Model):
    user_id = models.CharField(max_length=100)
    text = models.TextField()
    interpretation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Сон от {self.user_id}"
