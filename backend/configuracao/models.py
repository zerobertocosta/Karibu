# backend/configuracao/models.py

from django.db import models
from django.conf import settings

import uuid

class Estabelecimento(models.Model):
    """
    Representa um estabelecimento (restaurante, bar, cafeteria, etc.) dentro do sistema.
    Cada dado sensível no sistema será vinculado a um Estabelecimento.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255, unique=True, verbose_name="Nome do Estabelecimento")
    cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True, verbose_name="CNPJ")
    endereco = models.CharField(max_length=255, null=True, blank=True, verbose_name="Endereço")
    telefone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone")
    email_contato = models.EmailField(max_length=255, null=True, blank=True, verbose_name="Email de Contato")
    chave_pix = models.CharField(max_length=255, null=True, blank=True, verbose_name="Chave PIX")
    logotipo_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL do Logotipo")
    cor_primaria = models.CharField(max_length=7, default="#007bff", verbose_name="Cor Primária (HEX)")
    cor_secundaria = models.CharField(max_length=7, default="#6c757d", verbose_name="Cor Secundária (HEX)")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Estabelecimento"
        verbose_name_plural = "Estabelecimentos"
        ordering = ['nome'] # Ordenar por nome por padrão

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        # Opcional: Garante que o CNPJ seja salvo sem formatação, se fornecido
        if self.cnpj:
            self.cnpj = ''.join(filter(str.isdigit, self.cnpj))
        super().save(*args, **kwargs)

# backend/configuracao/models.py
# (Seu código existente do modelo Estabelecimento e outros viria acima deste)

# NOVO MODELO: AssinaturaEstabelecimento
class AssinaturaEstabelecimento(models.Model):
    ESTADO_CHOICES = [
        ('ATIVA', 'Ativa'),
        ('TESTE', 'Em Período de Teste'),
        ('CANCELADA', 'Cancelada'),
        ('SUSPENSA', 'Suspensa'),
        ('FINALIZADA', 'Finalizada'), # Ex: período contratado chegou ao fim
    ]
    FORMA_PAGAMENTO_CHOICES = [
        ('CARTAO', 'Cartão de Crédito/Débito'),
        ('BOLETO', 'Boleto Bancário'),
        ('PIX', 'Pix'),
        ('TRANSFERENCIA', 'Transferência Bancária'),
        ('OUTRO', 'Outro'),
    ]

    estabelecimento = models.ForeignKey(
        'configuracao.Estabelecimento', # Referência ao seu modelo Estabelecimento
        on_delete=models.CASCADE,
        related_name='historico_assinaturas',
        verbose_name='Estabelecimento'
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Referência ao seu modelo de Usuário (Gestor ou Admin)
        on_delete=models.SET_NULL, # Se o vendedor for excluído, não apaga o histórico de vendas
        null=True,
        blank=True,
        related_name='vendas_concluidas',
        verbose_name='Vendedor'
    )
    data_ativacao = models.DateField(
        verbose_name='Data de Ativação'
    )
    data_desativacao = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Desativação'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='TESTE',
        verbose_name='Estado da Assinatura'
    )
    valor_ativacao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Valor de Ativação/Configuração Inicial'
    )
    valor_mensal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Valor Mensal da Assinatura'
    )
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        null=True,
        blank=True,
        verbose_name='Forma de Pagamento'
    )
    observacoes = models.TextField(
        null=True,
        blank=True,
        verbose_name='Observações'
    )
    data_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Registro'
    )

    class Meta:
        verbose_name = 'Assinatura do Estabelecimento'
        verbose_name_plural = 'Assinaturas dos Estabelecimentos'

    def __str__(self):
        return f"Assinatura {self.get_estado_display()} para {self.estabelecimento.nome} ({self.data_ativacao} - {self.data_desativacao if self.data_desativacao else 'Atual'})"

    def save(self, *args, **kwargs):
        if self.data_desativacao and self.data_desativacao < self.data_ativacao:
            from django.core.exceptions import ValidationError
            raise ValidationError("A data de desativação não pode ser anterior à data de ativação.")
        super().save(*args, **kwargs)
