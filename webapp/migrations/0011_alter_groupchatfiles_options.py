# Generated by Django 4.2.6 on 2023-10-10 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0010_alter_groupchatfiles_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groupchatfiles',
            options={'ordering': ['-id'], 'verbose_name': 'файл для гр.чата', 'verbose_name_plural': 'файлы для гр.чатов'},
        ),
    ]
