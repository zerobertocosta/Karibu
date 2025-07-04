# backend/configuracao/admin.py

from django.contrib import admin
from .models import Estabelecimento

@admin.register(Estabelecimento)
class EstabelecimentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'cidade', 'pais', 'ativo', 'data_cadastro')
    list_filter = ('ativo', 'pais', 'cidade')
    search_fields = ('nome', 'email', 'contato', 'endereco')
    # Campos de imagem podem ser gerenciados via admin, certifique-se de ter Pillow instalado:
    # pip install Pillow