# backend/configuracao/admin.py

from django.contrib import admin
from .models import Estabelecimento

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