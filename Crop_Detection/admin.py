from django.contrib import admin
from .models import Feedback, ScanHistory, ContactMessage


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "email", "rating", "category")
    list_filter = ("category", "rating", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("submitted_at", "name", "email", "subject", "is_read")
    list_filter = ("is_read", "submitted_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "submitted_at")
    ordering = ("-submitted_at",)

    # Allow marking messages as read directly from the list view
    actions = ["mark_as_read", "mark_as_unread"]

    @admin.action(description="Mark selected messages as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected messages as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)


@admin.register(ScanHistory)
class ScanHistoryAdmin(admin.ModelAdmin):
    list_display = ("scanned_at", "original_name", "disease", "confidence")
    list_filter = ("disease", "scanned_at")
    search_fields = ("original_name", "disease")
    readonly_fields = ("scanned_at", "original_name", "image_path", "disease", "confidence", "all_predictions")
    ordering = ("-scanned_at",)
