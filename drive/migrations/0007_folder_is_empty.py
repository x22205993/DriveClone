# Generated by Django 5.0.3 on 2024-04-04 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0006_alter_file_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='is_empty',
            field=models.BooleanField(default=True),
        ),
    ]
