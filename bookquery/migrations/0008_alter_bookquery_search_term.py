# Generated by Django 4.1 on 2024-12-07 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookquery', '0007_alter_downloadcount_num_downloads'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookquery',
            name='search_term',
            field=models.CharField(max_length=1000, verbose_name='Search for a book by title, author, or both.'),
        ),
    ]
