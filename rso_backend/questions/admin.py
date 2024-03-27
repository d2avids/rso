from django.utils.safestring import mark_safe
from django.contrib import admin
from questions.models import Question, AnswerOption, Attempt, UserAnswer


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 0
    can_delete = True
    fields = ('text', 'image', 'is_correct')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'block', 'image_tag')
    search_fields = ('title', 'block')
    list_filter = ('block',)
    inlines = [AnswerOptionInline]

    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" height="auto" />')
        return "No Image"
    image_tag.short_description = 'Image'


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct', 'image_tag')
    search_fields = ('text', 'question__title')
    list_filter = ('is_correct', 'question__block')

    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" height="auto" />')
        return "No Image"
    image_tag.short_description = 'Image'


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'category')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'category')
    list_filter = ('timestamp', 'category')
    readonly_fields = ('user', 'timestamp', 'category', 'questions')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'answer_option')
    search_fields = ('attempt__user__username', 'question__title', 'answer_option__text')
    list_filter = ('attempt__category', 'question__block')
    readonly_fields = ('attempt', 'question', 'answer_option')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
