# Generated by Django 5.2.4 on 2025-07-08 21:25

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Estabelecimento',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=255, unique=True, verbose_name='Nome do Estabelecimento')),
                ('cnpj', models.CharField(blank=True, max_length=18, null=True, unique=True, verbose_name='CNPJ')),
                ('endereco', models.CharField(blank=True, max_length=255, null=True, verbose_name='Endereço')),
                ('telefone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Telefone')),
                ('email_contato', models.EmailField(blank=True, max_length=255, null=True, verbose_name='Email de Contato')),
                ('chave_pix', models.CharField(blank=True, max_length=255, null=True, verbose_name='Chave PIX')),
                ('logotipo_url', models.URLField(blank=True, max_length=500, null=True, verbose_name='URL do Logotipo')),
                ('cor_primaria', models.CharField(default='#007bff', max_length=7, verbose_name='Cor Primária (HEX)')),
                ('cor_secundaria', models.CharField(default='#6c757d', max_length=7, verbose_name='Cor Secundária (HEX)')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Última Atualização')),
            ],
            options={
                'verbose_name': 'Estabelecimento',
                'verbose_name_plural': 'Estabelecimentos',
                'ordering': ['nome'],
            },
        ),
    ]
