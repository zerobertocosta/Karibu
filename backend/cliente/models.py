# backend/cliente/models.py

from django.db import models
from configuracao.models import Estabelecimento # Importa o modelo Estabelecimento

class Cliente(models.Model):
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.CASCADE,
        related_name='clientes',
        verbose_name='Estabelecimento'
    )
    nome_completo = models.CharField(max_length=200)
    email = models.EmailField(max_length=255, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True,
                           help_text="CPF do cliente (opcional, para identificação única)")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        # Garante que a combinação de CPF (se existir) e estabelecimento seja única,
        # ou nome_completo e estabelecimento se CPF for nulo.
        # Mais tarde, podemos refinar isso para uma validação mais complexa
        # única por estabelecimento, permitindo o mesmo nome/CPF em estabelecimentos diferentes.
        unique_together = (('cpf', 'estabelecimento'), ('nome_completo', 'estabelecimento'))
        ordering = ['nome_completo']

    def __str__(self):
        return f"{self.nome_completo} ({self.estabelecimento.nome})"

    def clean(self):
        from django.core.exceptions import ValidationError
        # Se o CPF for fornecido, garante que é único por estabelecimento.
        # Se não houver CPF, o unique_together cuidará da combinação nome_completo/estabelecimento.
        if self.cpf:
            # Remove caracteres não numéricos do CPF para validação
            cleaned_cpf = ''.join(filter(str.isdigit, self.cpf))
            if len(cleaned_cpf) != 11:
                raise ValidationError({'cpf': 'CPF deve conter 11 dígitos numéricos.'})
            self.cpf = cleaned_cpf # Salva o CPF limpo

            # Validação extra para CPF único por estabelecimento se o unique_together não pegar
            if self.estabelecimento:
                query = Cliente.objects.filter(cpf=self.cpf, estabelecimento=self.estabelecimento)
                if self.pk: # Se estiver atualizando um cliente existente
                    query = query.exclude(pk=self.pk)
                if query.exists():
                    raise ValidationError({'cpf': 'Este CPF já está cadastrado para este estabelecimento.'})

    def save(self, *args, **kwargs):
        self.full_clean() # Executa o método clean() antes de salvar
        super().save(*args, **kwargs)