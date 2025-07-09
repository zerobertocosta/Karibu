# backend/mesa/admin.py

from django.contrib import admin
from .models import Mesa

# Register your models here.

class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'capacidade', 'status', 'get_estabelecimento_nome', 'data_criacao', 'data_atualizacao')
    list_filter = ('status', 'capacidade', 'estabelecimento') # Filtros no painel admin
    search_fields = ('numero', 'descricao') # Campos para pesquisa
    # Campos que podem ser editados diretamente na lista
    list_editable = ('status', 'capacidade')

    # Campo de relacionamento cru/autocompletar para Estabelecimento (para superusuários)
    raw_id_fields = ('estabelecimento',)

    # Método para exibir o nome do estabelecimento na list_display
    def get_estabelecimento_nome(self, obj):
        return obj.estabelecimento.nome if obj.estabelecimento else 'N/A'
    get_estabelecimento_nome.short_description = 'Estabelecimento' # Nome da coluna no admin

    # Sobrescreve o queryset para filtrar por estabelecimento do usuário logado
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento:
            return qs.filter(estabelecimento=request.user.perfil.estabelecimento)
        return qs

    # Sobrescreve o formulário para garantir que o estabelecimento seja pré-preenchido
    # ou filtrado para usuários não superusuários
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento:
            user_estabelecimento = request.user.perfil.estabelecimento
            # Filtra o queryset do campo 'estabelecimento' para mostrar apenas o estabelecimento do usuário
            if 'estabelecimento' in form.base_fields:
                form.base_fields['estabelecimento'].queryset = form.base_fields['estabelecimento'].queryset.filter(
                    id=user_estabelecimento.id
                )
                # Preenche o valor inicial se for um novo objeto e o campo não tiver valor
                if not obj:
                    form.base_fields['estabelecimento'].initial = user_estabelecimento.id
                # Desabilita botões de adicionar/alterar/deletar relacionamento para o campo estabelecimento
                form.base_fields['estabelecimento'].widget.can_add_related = False
                form.base_fields['estabelecimento'].widget.can_change_related = False
                form.base_fields['estabelecimento'].widget.can_delete_related = False
        return form

    # Sobrescreve o método save_model para garantir que o estabelecimento seja definido automaticamente
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.estabelecimento:
            if hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento:
                obj.estabelecimento = request.user.perfil.estabelecimento
        super().save_model(request, obj, form, change)


admin.site.register(Mesa, MesaAdmin)