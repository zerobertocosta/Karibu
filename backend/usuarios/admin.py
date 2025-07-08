# backend/usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil, Estabelecimento # Importar Estabelecimento também para o admin customizado

# Remover o registro padrão de User ANTES de registrar o nosso customizado
admin.site.unregister(User)

# Define um inline admin para o modelo Perfil, para ser exibido na página do User
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'perfil'
    fk_name = 'user'
    # Os campos 'id', 'data_criacao', 'data_atualizacao' serão apenas leitura
    readonly_fields = ('id', 'data_criacao', 'data_atualizacao',)
    # Adicionando o Estabelecimento para seleção
    fieldsets = (
        (None, {
            'fields': ('estabelecimento', 'papel')
        }),
        ('Metadados do Perfil', {
            'fields': ('id', 'data_criacao', 'data_atualizacao')
        }),
    )

    # Filtrar o queryset de estabelecimentos para mostrar apenas estabelecimentos ativos
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "estabelecimento":
            kwargs["queryset"] = Estabelecimento.objects.filter(ativo=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Define uma nova classe de administração de usuários
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_estabelecimento_nome', 'get_papel')
    list_select_related = ('perfil',) # Otimiza o carregamento do perfil

    # Adiciona 'estabelecimento' e 'papel' aos campos de busca
    search_fields = ('username', 'email', 'first_name', 'last_name', 'perfil__estabelecimento__nome', 'perfil__papel')
    # Adiciona 'is_staff' e 'papel' aos filtros da lista
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'perfil__papel', 'perfil__estabelecimento__nome')

    # CORREÇÃO: Removendo a linha do fieldsets duplicado,
    # pois os campos do perfil são adicionados via PerfilInline.
    # E 'is_active' já é tratado pelos fieldsets padrão do BaseUserAdmin.
    # fieldsets = BaseUserAdmin.fieldsets + (
    #     ('Informações do Perfil Karibu', {'fields': ('is_active',)}),
    # )
    # Mantemos apenas os fieldsets originais do BaseUserAdmin.

    # Se você precisar adicionar ou reorganizar outros campos do modelo User (não do Perfil),
    # você precisaria reconstruir os fieldsets aqui, garantindo a unicidade dos campos.
    # Mas para o nosso caso, com o inline, não precisamos mais dessa linha.

    # Métodos para exibir o nome do estabelecimento e o papel na listagem de usuários
    def get_estabelecimento_nome(self, obj):
        return obj.perfil.estabelecimento.nome if hasattr(obj, 'perfil') and obj.perfil.estabelecimento else 'N/A'
    get_estabelecimento_nome.short_description = 'Estabelecimento'

    def get_papel(self, obj):
        return obj.perfil.get_papel_display() if hasattr(obj, 'perfil') else 'N/A'
    get_papel.short_description = 'Papel'