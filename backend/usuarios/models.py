# backend/usuarios/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from configuracao.models import Estabelecimento # Importar o modelo Estabelecimento
import uuid

# Se você quiser estender o User padrão do Django, a melhor prática é definir AUTH_USER_MODEL
# no settings.py e usar um modelo customizado que herda de AbstractUser.
# Por simplicidade inicial e para focar no multi-tenant, vamos usar um modelo de Perfil
# que estende o User padrão do Django.

class Perfil(models.Model):
    """
    Modelo de perfil que estende o User padrão do Django, adicionando
    o vínculo com um Estabelecimento e um campo para o papel do usuário.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'auth.User', # Referencia o User padrão do Django
        on_delete=models.CASCADE,
        related_name='perfil', # Nome para acesso reverso (user.perfil)
        verbose_name="Usuário"
    )
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE, # Se o estabelecimento for deletado, os perfis vinculados também são
        related_name='perfis',
        verbose_name="Estabelecimento"
    )
    # Definir as opções para o papel do usuário
    GESTOR = 'gestor'
    GARCOM = 'garcom'
    COZINHEIRO = 'cozinheiro'
    CAIXA = 'caixa'
    ROLE_CHOICES = [
        (GESTOR, 'Gestor'),
        (GARCOM, 'Garçom'),
        (COZINHEIRO, 'Cozinheiro'),
        (CAIXA, 'Caixa'),
    ]
    papel = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=GARCOM, # Papel padrão, pode ser ajustado
        verbose_name="Papel do Usuário"
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuário"
        # Garante que um usuário só possa ter um perfil
        unique_together = ('user',)

    def __str__(self):
        return f"{self.user.username} ({self.papel} - {self.estabelecimento.nome})"

    # Métodos auxiliares para verificar o papel
    @property
    def is_gestor(self):
        return self.papel == self.GESTOR

    @property
    def is_garcom(self):
        return self.papel == self.GARCOM

    @property
    def is_cozinheiro(self):
        return self.papel == self.COZINHEIRO

    @property
    def is_caixa(self):
        return self.papel == self.CAIXA