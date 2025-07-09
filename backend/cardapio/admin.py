# backend/cardapio/admin.py

from django.contrib import admin
from .models import Categoria, ItemCardapio

# Register your models here.

# @admin.register(Categoria)
# class CategoriaAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'estabelecimento', 'ativa', 'ordem', 'data_criacao')
#     list_filter = ('estabelecimento', 'ativa')
#     search_fields = ('nome', 'descricao')
#     raw_id_fields = ('estabelecimento',) # Melhora a seleção de estabelecimento para muitos itens

# @admin.register(ItemCardapio)
# class ItemCardapioAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'categoria', 'estabelecimento', 'preco', 'disponivel', 'ordem')
#     list_filter = ('categoria__estabelecimento', 'disponivel', 'categoria') # Filtrar por estabelecimento da categoria
#     search_fields = ('nome', 'descricao')
#     raw_id_fields = ('estabelecimento', 'categoria')
#     autocomplete_fields = ['categoria'] # Ajuda a pesquisar categorias

# Usando ModelAdmin customizado para melhor UX e verificação de estabelecimento
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_estabelecimento_nome', 'ativa', 'ordem', 'data_criacao')
    list_filter = ('ativa',)
    search_fields = ('nome', 'descricao')
    # O raw_id_fields é bom para muitos estabelecimentos, mas para o admin
    # garantimos que o estabelecimento padrão do usuário (se não for superuser) seja preenchido
    # raw_id_fields = ('estabelecimento',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento:
            return qs.filter(estabelecimento=request.user.perfil.estabelecimento)
        return qs

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.estabelecimento:
            if hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento:
                obj.estabelecimento = request.user.perfil.estabelecimento
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento:
            # Não permite que um usuário de estabelecimento altere o campo estabelecimento
            # ou veja outros estabelecimentos ao criar/editar categorias
            if 'estabelecimento' in form.base_fields:
                form.base_fields['estabelecimento'].queryset = form.base_fields['estabelecimento'].queryset.filter(
                    id=request.user.perfil.estabelecimento.id
                )
                if not obj: # Ao criar um novo, preenche o valor padrão
                    form.base_fields['estabelecimento'].initial = request.user.perfil.estabelecimento.id
                form.base_fields['estabelecimento'].widget.can_add_related = False
                form.base_fields['estabelecimento'].widget.can_change_related = False
                form.base_fields['estabelecimento'].widget.can_delete_related = False

        return form

    def get_estabelecimento_nome(self, obj):
        return obj.estabelecimento.nome if obj.estabelecimento else 'N/A'
    get_estabelecimento_nome.short_description = 'Estabelecimento'


class ItemCardapioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_categoria_nome', 'get_estabelecimento_nome', 'preco', 'disponivel', 'ordem')
    list_filter = ('disponivel', 'categoria', 'estabelecimento')
    search_fields = ('nome', 'descricao')
    autocomplete_fields = ['categoria'] # Requer que Categoria seja registrada com search_fields
    # raw_id_fields = ('estabelecimento', 'categoria',) # Bom para muitos itens

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento:
            return qs.filter(estabelecimento=request.user.perfil.estabelecimento)
        return qs

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.estabelecimento:
            if hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento:
                obj.estabelecimento = request.user.perfil.estabelecimento
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and hasattr(request.user, 'perfil') and request.user.perfil.estabelecimento:
            user_estabelecimento = request.user.perfil.estabelecimento
            # Filtra o queryset de categoria para mostrar apenas as do estabelecimento do usuário
            form.base_fields['categoria'].queryset = form.base_fields['categoria'].queryset.filter(
                estabelecimento=user_estabelecimento
            )
            # Preenche o campo estabelecimento para usuários não superuser
            if 'estabelecimento' in form.base_fields:
                form.base_fields['estabelecimento'].queryset = form.base_fields['estabelecimento'].queryset.filter(
                    id=user_estabelecimento.id
                )
                if not obj:
                    form.base_fields['estabelecimento'].initial = user_estabelecimento.id
                form.base_fields['estabelecimento'].widget.can_add_related = False
                form.base_fields['estabelecimento'].widget.can_change_related = False
                form.base_fields['estabelecimento'].widget.can_delete_related = False
        return form

    def get_categoria_nome(self, obj):
        return obj.categoria.nome if obj.categoria else 'N/A'
    get_categoria_nome.short_description = 'Categoria'

    def get_estabelecimento_nome(self, obj):
        return obj.estabelecimento.nome if obj.estabelecimento else 'N/A'
    get_estabelecimento_nome.short_description = 'Estabelecimento'


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(ItemCardapio, ItemCardapioAdmin)