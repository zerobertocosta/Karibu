# backend/cliente/admin.py
from django.contrib import admin
from .models import Cliente # Importa o modelo Cliente
from django.contrib.auth import get_user_model # Para acessar o modelo de usuário

User = get_user_model() # Obtém o modelo de usuário atual

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Configuração do painel de administração para o modelo Cliente.
    """
    # Define quais campos serão exibidos na lista de clientes no admin
    list_display = (
        'celular', # O novo PK e identificador principal (se for unique)
        'nome_completo',
        'get_estabelecimento_nome', # Método auxiliar para exibir o nome do estabelecimento
        'data_cadastro',
        'data_atualizacao'
    )

    # Define campos pelos quais se pode pesquisar clientes
    search_fields = (
        'celular',
        'nome_completo',
        'logradouro',
        'bairro',
        'cidade',
        'cep'
    )

    # Define campos que podem ser usados para filtrar a lista de clientes
    list_filter = (
        'estabelecimento',
        'data_cadastro',
        'cidade',
        'estado'
    )

    # Não incluiremos list_editable aqui para evitar edição direta de campos sensíveis
    # e porque 'celular' é chave primária (não editável em list_editable)

    # Agrupamento de campos no formulário de detalhes do cliente para melhor organização
    fieldsets = (
        (None, {
            # REMOVIDOS: 'password' (não existe mais no modelo Cliente)
            #           'complemento' (não existe no modelo Cliente)
            'fields': (
                'celular',
                'nome_completo',
                'estabelecimento',
                'foto_cliente',
                'data_nascimento'
            )
        }),
        ('Endereço', {
            # REMOVIDO: 'complemento' (não existe no modelo Cliente)
            'fields': (
                'logradouro',
                'numero',
                'bairro',
                'cidade',
                'estado',
                'cep'
            ),
            'classes': ('collapse',), # Opcional: faz o fieldset ser colapsável por padrão
        }),
        ('Datas', {
            'fields': (
                'data_cadastro',
                'data_atualizacao'
            ),
            'classes': ('collapse',),
        }),
    )

    # Usa autocomplete_fields para o campo 'estabelecimento'.
    # Isso transformará o campo de seleção em um campo de texto com autocompletar
    # que exibe o nome do estabelecimento (do __str__ do modelo Estabelecimento)
    # e permite pesquisa. Requer 'search_fields' configurado no EstabelecimentoAdmin.
    autocomplete_fields = ['estabelecimento']

    # Define campos que serão somente leitura no formulário de edição/criação
    readonly_fields = ('data_cadastro', 'data_atualizacao')

    # =========================================================================
    # MÉTODO AUXILIAR PARA list_display
    # =========================================================================
    def get_estabelecimento_nome(self, obj):
        """ Retorna o nome do estabelecimento para exibição na list_display. """
        return obj.estabelecimento.nome if obj.estabelecimento else 'N/A'
    get_estabelecimento_nome.short_description = 'Estabelecimento Associado' # Título da coluna no admin

    # =========================================================================
    # Lógica de Multi-Tenant e Permissões (já estava no seu código, mantida e ajustada)
    # =========================================================================
    # Sobrescreve o queryset para filtrar por estabelecimento do usuário logado
    # (Usuários não superusuários verão apenas os clientes de seu próprio estabelecimento)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and \
           hasattr(request.user, 'perfil') and \
           request.user.perfil.estabelecimento:
            return qs.filter(estabelecimento=request.user.perfil.estabelecimento)
        return qs

    # Sobrescreve o formulário para garantir que o campo estabelecimento seja pré-preenchido
    # ou filtrado para usuários não superusuários e desabilita botões de relacionamento
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and \
           hasattr(request.user, 'perfil') and \
           request.user.perfil.estabelecimento:
            user_estabelecimento = request.user.perfil.estabelecimento

            # Filtra o queryset do campo 'estabelecimento' para mostrar apenas o estabelecimento do usuário
            if 'estabelecimento' in form.base_fields:
                form.base_fields['estabelecimento'].queryset = \
                    form.base_fields['estabelecimento'].queryset.filter(id=user_estabelecimento.id)

                # Preenche o valor inicial se for um novo objeto e o campo não tiver valor
                if not obj: # Para criação de novo objeto
                    form.base_fields['estabelecimento'].initial = user_estabelecimento.id

                # Desabilita botões de adicionar/alterar/deletar relacionamento para o campo estabelecimento
                form.base_fields['estabelecimento'].widget.can_add_related = False
                form.base_fields['estabelecimento'].widget.can_change_related = False
                form.base_fields['estabelecimento'].widget.can_delete_related = False
        return form

    # Sobrescreve o método save_model para garantir que o estabelecimento seja definido automaticamente
    # para usuários não superusuários, se ainda não estiver definido.
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.estabelecimento:
            if hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento:
                obj.estabelecimento = request.user.perfil.estabelecimento
        super().save_model(request, obj, form, change)