from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # Campos que aparecerão na lista de clientes no admin
    list_display = ('id', 'nome', 'email', 'telefone', 'data_cadastro', 'ativo')
    # Campos pelos quais você pode filtrar a lista
    list_filter = ('ativo', 'data_cadastro')
    # Campos pelos quais você pode pesquisar (adicione 'id' para poder pesquisar pelo ID)
    search_fields = ('id', 'nome', 'email', 'telefone')
    # Campos que se tornam links para a página de edição
    list_display_links = ('id', 'nome')