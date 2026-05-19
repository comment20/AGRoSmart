from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_from_user = models.BooleanField(default=True) # True if from user, False if from bot

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        sender = "User" if self.is_from_user else "Bot"
        return f"{sender} ({self.timestamp.strftime('%H:%M')}): {self.message[:50]}..."