# Generated by Django 4.2.6 on 2023-10-12 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0013_groupchatfiles_file_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='groupchats',
            old_name='group_tlg_id',
            new_name='group_tg_id',
        ),
        migrations.AlterField(
            model_name='groupchats',
            name='link',
            field=models.URLField(blank=True, null=True, verbose_name='ссылка'),
        ),
    ]
