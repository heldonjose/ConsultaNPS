# Generated by Django 3.1.3 on 2020-11-15 17:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True)),
                ('date_modificado', models.DateTimeField(auto_now=True, null=True)),
                ('nome', models.CharField(help_text='Nome', max_length=255)),
                ('email', models.CharField(help_text='Email', max_length=255)),
                ('senha', models.CharField(help_text='SENHA', max_length=100)),
                ('tipo', models.CharField(choices=[('PESQUISADOR', 'PESQUISADOR'), ('PESQUISADO', 'PESQUISADO')], max_length=50, verbose_name='TIPO')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='usuario', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Usuário',
                'verbose_name_plural': 'Usuários',
                'ordering': ('nome',),
            },
        ),
    ]
