from django.contrib import admin
from .models import Prediction, CropPrediction

class PredictionAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'soil_type', 'confidence', 'location_name')
    list_filter = ('soil_type', 'user', 'timestamp')
    search_fields = ('user__username', 'soil_type', 'location_name')
    date_hierarchy = 'timestamp'

class CropPredictionAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'predicted_crop', 'temperature', 'ph', 'humidity')
    list_filter = ('predicted_crop', 'user', 'timestamp')
    search_fields = ('user__username', 'predicted_crop')
    date_hierarchy = 'timestamp'

admin.site.register(Prediction, PredictionAdmin)
admin.site.register(CropPrediction, CropPredictionAdmin)
