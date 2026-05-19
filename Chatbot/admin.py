from django.contrib import admin
from .models import ChatMessage

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'is_from_user', 'message')
    list_filter = ('is_from_user', 'user')
    search_fields = ('message', 'user__username')
    readonly_fields = ('timestamp', 'user', 'message', 'is_from_user')

admin.site.register(ChatMessage, ChatMessageAdmin)