# Generated by Django 4.1 on 2022-08-04 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookquery', '0002_bookquery_search_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookquery',
            name='search_type',
            field=models.CharField(choices=[('Fiction', 'Fiction'), ('Non-fiction', 'Non-fiction')], default='Fiction', max_length=500, verbose_name='Choose fiction or non-fiction.'),
        ),
    ]