# backend/mesa/admin.py

from django.contrib import admin
from .models import Mesa # Importa o modelo Mesa do próprio app 'mesa'

# Registra o modelo Mesa com uma configuração customizada para o Admin
@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    # Campos a serem exibidos na lista de objetos no painel do Admin
    list_display = ('numero', 'capacidade', 'disponivel', 'data_cadastro')
    
    # Campos pelos quais a lista de objetos pode ser filtrada
    list_filter = ('disponivel', 'capacidade')
    
    # Campos pelos quais a lista de objetos pode ser pesquisada
    search_fields = ('numero',)
    
    # Ordem padrão de exibição dos objetos
    ordering = ('numero',)
