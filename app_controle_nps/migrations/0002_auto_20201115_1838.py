# Generated by Django 3.1.3 on 2020-11-15 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_controle_nps', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pesquisa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True)),
                ('date_modificado', models.DateTimeField(auto_now=True, null=True)),
                ('descricao', models.CharField(max_length=255, verbose_name='Descrição')),
            ],
            options={
                'verbose_name': 'Pesquisa',
                'verbose_name_plural': 'Pesquisas',
                'ordering': ('descricao',),
            },
        ),
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.CharField(help_text='Email, também usulizado como login', max_length=255),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='nome',
            field=models.CharField(help_text='Nome do Usuário', max_length=255),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='senha',
            field=models.CharField(help_text='Senha do Usuário', max_length=100),
        ),
        migrations.CreateModel(
            name='Questao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True)),
                ('date_modificado', models.DateTimeField(auto_now=True, null=True)),
                ('descricao', models.CharField(max_length=255, verbose_name='Descrição')),
                ('pesquisa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_controle_nps.pesquisa')),
            ],
            options={
                'verbose_name': 'Questão',
                'verbose_name_plural': 'Questões',
                'ordering': ('pesquisa',),
            },
        ),
    ]
