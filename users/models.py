import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    image = models.ImageField(upload_to='users_images', blank=True, null=True, verbose_name='Аватар')
    phone_number = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'user'
        verbose_name = 'Пользователя'
        verbose_name_plural = "Пользователи"

    def save(self, *args, **kwargs):
        # Если объект уже существует в базе данных (обновление)
        if self.pk:
            # Получаем старую версию объекта из базы данных
            old_instance = User.objects.get(pk=self.pk)
            # Если старое изображение есть и оно отличается от нового
            if old_instance.image and old_instance.image != self.image:
                image_path = os.path.join(settings.MEDIA_ROOT, old_instance.image.name)
                if os.path.isfile(image_path):
                    os.remove(image_path)  # Удаляем старый файл

        # Вызываем стандартный метод save
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username