# Generated by Django 4.2.7 on 2024-10-02 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_alter_categories_table'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categories',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
    ]
