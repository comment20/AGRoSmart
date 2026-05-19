from django.db import models
from django.contrib.auth.models import User # Import User model

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # Make user field nullable
    timestamp = models.DateTimeField(auto_now_add=True)
    image_name = models.CharField(max_length=255)
    soil_type = models.CharField(max_length=100) # Increase max_length
    confidence = models.FloatField()
    # New fields for location
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Prediction by {self.user.username if self.user else 'Anonymous'} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}: {self.soil_type} ({self.confidence:.2f}%)"

    class Meta:
        ordering = ['timestamp'] # Order by newest first

class CropPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField()
    ph = models.FloatField()
    humidity = models.FloatField()
    nitrogen = models.FloatField()
    potassium = models.FloatField()
    phosphorus = models.FloatField()
    rainfall = models.FloatField()
    predicted_crop = models.CharField(max_length=100)
    # New fields for location
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Crop Prediction by {self.user.username if self.user else 'Anonymous'} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}: {self.predicted_crop}"

    class Meta:
        ordering = ['-timestamp'] # Order by newest first