# backend/cliente/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password

# Importa o modelo Estabelecimento do seu app de configuracao
from configuracao.models import Estabelecimento

class Cliente(models.Model):
    # O celular será a chave única e principal
    celular = models.CharField(
        max_length=20, # Mantido em 20 para flexibilidade, inclui DDI, DDD e 9 dígitos
        unique=True,  # Garante que o celular seja único em toda a base de clientes
        primary_key=True,  # Define o celular como chave primária
        help_text="Número de celular do cliente (chave única)",
        verbose_name="Celular"
    )
    
    # Senha para o cliente cadastrar
    password = models.CharField(
        max_length=128,  # Tamanho padrão para senhas criptografadas
        verbose_name="Senha"
    )

    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='clientes',
        verbose_name='Estabelecimento'
    )
    
    nome_completo = models.CharField(
        max_length=200,
        verbose_name="Nome Completo"
    )
    
    foto_cliente = models.ImageField(
        upload_to='clientes/fotos/',  # Onde as fotos serão salvas no MEDIA_ROOT
        blank=True,
        null=True,
        verbose_name="Foto do Cliente"
    )
    
    data_nascimento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Nascimento"
    )

    # Campos para endereço completo
    logradouro = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Logradouro"
    )
    numero = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Número"
    )
    complemento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Complemento"
    )
    bairro = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Bairro"
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cidade"
    )
    estado = models.CharField(
        max_length=2,  # Ex: SP, RJ
        blank=True,
        null=True,
        verbose_name="Estado"
    )
    cep = models.CharField(
        max_length=9,  # Ex: 12345-678
        blank=True,
        null=True,
        verbose_name="CEP"
    )

    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome_completo']

    def __str__(self):
        return f"{self.nome_completo} ({self.celular})"

    def clean(self):
        if self.celular:
            cleaned_celular = ''.join(filter(str.isdigit, self.celular))
            # Ajustado para permitir 10, 11 (DDD + número) ou até 13 (DDI + DDD + número) dígitos.
            # O DDI do Brasil é 55.
            if not (10 <= len(cleaned_celular) <= 13):
                raise ValidationError({'celular': _('O celular deve conter entre 10 e 13 dígitos numéricos (incluindo DDI e DDD, se aplicável).')})
            self.celular = cleaned_celular # Salva o celular limpo

        if self.celular and self.estabelecimento:
            existing_clientes = Cliente.objects.filter(celular=self.celular)
            if self.pk:
                existing_clientes = existing_clientes.exclude(pk=self.pk)
            
            # A validação abaixo agora é mais um aviso, pois o celular é PK e já garante unicidade.
            # No entanto, se o cliente só pode estar em UM estabelecimento, isso ainda é relevante.
            if existing_clientes.exists() and existing_clientes.first().estabelecimento != self.estabelecimento:
                raise ValidationError({
                    'estabelecimento': _('Este celular já está registrado em outro estabelecimento.')
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # Executa o método clean() antes de salvar

        # Hash da senha se ela foi definida ou alterada
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        """
        Retorna True se a senha bruta fornecida corresponder à senha com hash.
        """
        return check_password(raw_password, self.password)