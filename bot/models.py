from django.db import models
from django.contrib.postgres.fields import ArrayField


# модель пользователя
class User(models.Model):
    chat_id = models.IntegerField()
    username = models.CharField(max_length=255)
    state = models.IntegerField()
    test_result = models.ForeignKey('Animal', on_delete=models.CASCADE, null=True)


# модель вопроса с ответами к каждому
class Question(models.Model):
    order_in_test = models.IntegerField()
    question = models.CharField(max_length=255)
    answers = ArrayField(
        models.CharField(max_length=255, blank=True),
        size=4
    )

    def __str__(self):
        return self.question


# модель животного с описанием результата и ответов для просчета результата
class Animal(models.Model):
    name = models.CharField(max_length=255)
    test_result = models.TextField()
    answers = ArrayField(
        models.CharField(max_length=255, blank=True),
        size=5
    )
    animal = models.ImageField(upload_to='images/', null=True)

    def __str__(self):
        return self.name


# модель отзыва от пользователя
class Review(models.Model):
    chat_id = models.IntegerField()
    username = models.CharField(max_length=255)
    review_text = models.TextField()
    published_data = models.DateTimeField(auto_now_add=True)
