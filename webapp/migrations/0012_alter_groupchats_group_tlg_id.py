# Generated by Django 4.2.6 on 2023-10-10 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0011_alter_groupchatfiles_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupchats',
            name='group_tlg_id',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='TG ID чата'),
        ),
    ]
