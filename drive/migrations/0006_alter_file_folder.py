# Generated by Django 5.0.3 on 2024-04-03 21:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0005_remove_storageitem_path_id_folder_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='folder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='drive.folder'),
        ),
    ]