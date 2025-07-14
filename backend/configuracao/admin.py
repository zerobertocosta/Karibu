# backend/configuracao/admin.py

from django.contrib import admin
from .models import Estabelecimento, AssinaturaEstabelecimento 


@admin.register(Estabelecimento)
class EstabelecimentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'email_contato', 'ativo', 'data_criacao')
    search_fields = ('nome', 'cnpj', 'email_contato')
    list_filter = ('ativo',)
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao') # Campos que não podem ser editados após a criação

    fieldsets = (
        (None, {
            'fields': ('nome', 'cnpj', 'ativo')
        }),
        ('Informações de Contato', {
            'fields': ('endereco', 'telefone', 'email_contato', 'chave_pix')
        }),
        ('Personalização Visual', {
            'fields': ('logotipo_url', 'cor_primaria', 'cor_secundaria')
        }),
        ('Metadados', {
            'fields': ('id', 'data_criacao', 'data_atualizacao')
        }),
    )

# NOVO REGISTRO: AssinaturaEstabelecimentoAdmin
@admin.register(AssinaturaEstabelecimento)
class AssinaturaEstabelecimentoAdmin(admin.ModelAdmin):
    list_display = (
        'estabelecimento', 'vendedor', 'data_ativacao', 'data_desativacao',
        'estado', 'valor_mensal', 'forma_pagamento', 'data_registro'
    )
    list_filter = (
        'estado', 'forma_pagamento', 'vendedor', 'data_ativacao', 'data_desativacao'
    )
    search_fields = (
        'estabelecimento__nome', 'vendedor__username', 'observacoes'
    )
    date_hierarchy = 'data_ativacao'
    fieldsets = (
        (None, {
            'fields': ('estabelecimento', 'vendedor', 'estado', 'observacoes')
        }),
        ('Período da Assinatura', {
            'fields': ('data_ativacao', 'data_desativacao')
        }),
        ('Valores e Pagamento', {
            'fields': ('valor_ativacao', 'valor_mensal', 'forma_pagamento')
        }),
    )