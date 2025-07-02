# backend/chamada/admin.py

from django.contrib import admin
from .models import ChamadaGarcom

# Registra o modelo ChamadaGarcom para ser visível no painel de administração do Django
@admin.register(ChamadaGarcom)
class ChamadaGarcomAdmin(admin.ModelAdmin):
    list_display = ('mesa', 'data_hora_chamada', 'atendida') # Campos a exibir na lista
    list_filter = ('atendida', 'data_hora_chamada') # Filtros na barra lateral
    search_fields = ('mesa__numero',) # Permite buscar por número da mesa
    readonly_fields = ('data_hora_chamada',) # Campo de data/hora é apenas para leitura
