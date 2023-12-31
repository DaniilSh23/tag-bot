# Generated by Django 4.2.6 on 2023-10-05 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentBills',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='сумма')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='когда создан')),
                ('pay_method', models.CharField(choices=[('to_card', 'перевод на карту')], verbose_name='способ оплаты')),
                ('status', models.CharField(choices=[('created', 'создан'), ('on_check', 'на проверке'), ('payed', 'оплачен'), ('close_without_pay', 'закрыт без оплаты')], default='created', verbose_name='статус')),
                ('file', models.FileField(null=True, upload_to='bill_files/', verbose_name='файл')),
                ('bot_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.botuser', verbose_name='юзер')),
            ],
            options={
                'verbose_name': 'счет на оплату',
                'verbose_name_plural': 'счета на оплату',
                'ordering': ['-id'],
            },
        ),
    ]
