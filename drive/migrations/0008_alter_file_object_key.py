# Generated by Django 5.0.3 on 2024-04-04 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0007_folder_is_empty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='object_key',
            field=models.CharField(max_length=300),
        ),
    ]
