# Generated by Django 4.1 on 2022-08-04 12:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bookquery', '0004_bookquerynonfiction_delete_bookquery'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_term', models.CharField(max_length=1000, verbose_name='Search for book by title, author, or both.')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('pages', models.IntegerField(blank=True, null=True)),
                ('search_type', models.CharField(choices=[('Fiction', 'Fiction'), ('Non-fiction', 'Non-fiction')], default='Fiction', max_length=500, verbose_name='Choose fiction or non-fiction.')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='query', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='BookQueryNonFiction',
        ),
    ]
