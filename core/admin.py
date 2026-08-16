from django.contrib import admin

from .models import Cabin, DailyCommitment, Member, Message


@admin.register(DailyCommitment)
class DailyCommitmentAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "is_completed", "updated_at")
    list_filter = ("is_completed", "date")
    search_fields = ("user__username", "user__email")


@admin.register(Cabin)
class CabinAdmin(admin.ModelAdmin):
    list_display = ("number", "gender", "age_range", "location")
    search_fields = ("number",)


class MemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "cabin", "role", "gender", "phone", "is_active")
    list_filter = ("role", "cabin", "gender", "is_active")
    search_fields = ("full_name", "phone", "user__username", "user__email")


admin.site.register(Member, MemberAdmin)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "body", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("sender__username", "recipient__username", "body")
