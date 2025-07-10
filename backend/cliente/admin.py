# backend/cliente/admin.py

from django.contrib import admin
from .models import Cliente # Importa o modelo Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Configuração do painel de administração para o modelo Cliente.
    """
    # Define quais campos serão exibidos na lista de clientes no admin
    # Removido 'ativo' pois não existe no modelo Cliente
    list_display = ('nome_completo', 'email', 'telefone', 'cpf', 'get_estabelecimento_nome', 'data_cadastro')

    # Define campos pelos quais se pode pesquisar clientes
    search_fields = ('nome_completo', 'email', 'telefone', 'cpf')

    # Define campos que podem ser usados para filtrar a lista de clientes
    # Removido 'ativo' pois não existe no modelo Cliente
    list_filter = ('estabelecimento', 'data_cadastro')

    # Define campos que podem ser editados diretamente na lista (cuidado com isso em produção)
    # Removido 'ativo' pois não existe no modelo Cliente
    list_editable = ('email', 'telefone')

    # =========================================================================
    # SOLUÇÃO PARA EXIBIR O NOME DO ESTABELECIMENTO NO FORMULÁRIO E PESQUISA
    # =========================================================================
    # Usa autocomplete_fields para o campo 'estabelecimento'.
    # Isso transformará o campo de seleção em um campo de texto com autocompletar
    # que exibe o nome do estabelecimento (do __str__ do modelo Estabelecimento)
    # e permite pesquisa. Requer 'search_fields' configurado no EstabelecimentoAdmin.
    autocomplete_fields = ['estabelecimento']

    # Se você tinha raw_id_fields descomentado antes, certifique-se de que esteja comentado ou removido:
    # raw_id_fields = ('estabelecimento',)
    # =========================================================================

    # Define campos que serão somente leitura no formulário de edição/criação
    # Adicionado 'data_atualizacao' se ele existe no seu modelo Cliente e você quer que seja readonly.
    readonly_fields = ('data_cadastro', 'data_atualizacao')

    # =========================================================================
    # MÉTODO AUXILIAR PARA list_display (INDENTAÇÃO CORRIGIDA)
    # =========================================================================
    # Este método DEVE estar dentro da classe ClienteAdmin e com a mesma indentação
    # das variáveis de classe acima (list_display, search_fields, etc.).
    def get_estabelecimento_nome(self, obj):
        """
        Retorna o nome do estabelecimento para exibição na list_display.
        """
        return obj.estabelecimento.nome if obj.estabelecimento else 'N/A'
    get_estabelecimento_nome.short_description = 'Estabelecimento Associado' # Título da coluna no admin


    # =========================================================================
    # Lógica de Multi-Tenant e Permissões (já estava no seu código, mantida)
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
                if not obj:
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

# A linha abaixo foi removida ou comentada, pois o registro já é feito pelo @admin.register
# admin.site.register(Cliente, ClienteAdmin)