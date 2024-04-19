from django.contrib import admin
from .models import Question, Animal, User, Review


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('order_in_test', 'question', 'answers')


class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'test_result', 'answers', 'animal')


class UserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'username', 'test_result')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('username', 'review_text', 'published_data')


admin.site.register(Question, QuestionAdmin)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Review, ReviewAdmin)
