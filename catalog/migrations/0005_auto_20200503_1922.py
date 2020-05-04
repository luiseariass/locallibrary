# Generated by Django 3.0.5 on 2020-05-04 00:22

from django.db import migrations, models
import gdstorage.storage


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_auto_20200428_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='book_data',
            field=models.FileField(null=True, storage=gdstorage.storage.GoogleDriveStorage(), upload_to='books'),
        ),
        migrations.AlterField(
            model_name='genre',
            name='name',
            field=models.CharField(help_text='nEter a book genre (e.g. Science Fiction)', max_length=200),
        ),
    ]
