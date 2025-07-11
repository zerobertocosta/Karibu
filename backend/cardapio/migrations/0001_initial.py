# Generated by Django 5.2.4 on 2025-07-08 23:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('configuracao', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('ativa', models.BooleanField(default=True)),
                ('ordem', models.IntegerField(default=0, help_text='Ordem de exibição da categoria no cardápio')),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('estabelecimento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorias', to='configuracao.estabelecimento', verbose_name='Estabelecimento')),
            ],
            options={
                'verbose_name': 'Categoria do Cardápio',
                'verbose_name_plural': 'Categorias do Cardápio',
                'ordering': ['ordem', 'nome'],
                'unique_together': {('nome', 'estabelecimento')},
            },
        ),
    ]
