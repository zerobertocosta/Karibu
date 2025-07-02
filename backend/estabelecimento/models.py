from django.db import models

class Estabelecimento(models.Model):
    nome = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Estabelecimento"
        verbose_name_plural = "Estabelecimentos"
        ordering = ['nome'] # Ordena por nome por padrão

    def __str__(self):
        return self.nome