# backend/mesas/mixins.py (CÓDIGO COMPLETO COM MAIS LOGS PARA DEPURAR)

import logging
from rest_framework.exceptions import PermissionDenied, ValidationError

logger = logging.getLogger(__name__) # <-- Mantenha esta linha

class MesaEstablishmentMixin:
    """
    Mixin específico para ViewSets de Mesa.
    Garante que as operações de CRUD para Mesa sejam vinculadas ao estabelecimento do usuário autenticado.
    Apenas superusuários ou usuários com perfil de 'Gestor' (baseado em is_gestor do Perfil)
    podem criar, atualizar e deletar mesas.
    Superusuários veem e gerenciam todas as mesas.
    Outros usuários veem as mesas do seu estabelecimento.
    """
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado.")

        if self.request.user.is_superuser:
            return super().get_queryset()

        if not hasattr(self.request.user, 'perfil') or self.request.user.perfil is None or not self.request.user.perfil.estabelecimento:
            raise PermissionDenied("Seu perfil de usuário não está vinculado a um estabelecimento.")

        # A visualização (GET) da lista de mesas é permitida para qualquer usuário do estabelecimento
        return super().get_queryset().filter(estabelecimento=self.request.user.perfil.estabelecimento)

    def _has_gestor_permission_for_write(self):
        """
        Verifica se o usuário tem permissão de escrita (criar/atualizar/excluir) para mesas.
        Baseia-se na propriedade 'is_gestor' do perfil do usuário.
        """
        user = self.request.user
        logger.info(f"--- DEPURAÇÃO DE PERMISSÃO DE ESCRITA PARA MESAS ---")
        logger.info(f"Usuário logado: {user.username if user.is_authenticated else 'Não Autenticado'}")
        logger.info(f"Usuário é superusuário: {user.is_superuser}")

        if user.is_superuser:
            logger.info("Resultado: Permissão concedida (Superusuário).")
            return True
        
        # Verifica se o usuário tem um perfil
        if not hasattr(user, 'perfil') or user.perfil is None:
            logger.warning(f"Usuário {user.username} não possui perfil associado.")
            logger.info("Resultado: Permissão negada (Sem perfil).")
            return False
        
        perfil = user.perfil
        logger.info(f"Perfil do usuário {user.username} - Papel: '{perfil.papel}', Estabelecimento ID: '{perfil.estabelecimento.id if perfil.estabelecimento else 'None'}'")
        logger.info(f"Perfil do usuário {user.username} - is_gestor: {perfil.is_gestor}")

        # Condição para gestor: tem perfil, o perfil é um gestor, e tem um estabelecimento vinculado
        if perfil.is_gestor and perfil.estabelecimento is not None:
            logger.info("Resultado: Permissão concedida (Usuário é Gestor com estabelecimento).")
            return True
            
        logger.info("Resultado: Permissão negada (Não é Gestor ou sem estabelecimento).")
        return False

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado para criar.")
        
        if not self._has_gestor_permission_for_write():
            raise PermissionDenied("Você não tem permissão para criar mesas. Apenas Superusuários e Gestores.")
        
        if not hasattr(self.request.user, 'perfil') or not self.request.user.perfil.estabelecimento:
            raise ValidationError({"detail": "Seu perfil de usuário não está vinculado a um estabelecimento."})

        final_establishment = self.request.user.perfil.estabelecimento
        serializer.save(estabelecimento=final_establishment)

    def perform_update(self, serializer):
        instance = self.get_object()

        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado para atualizar.")

        if not self._has_gestor_permission_for_write():
            raise PermissionDenied("Você não tem permissão para atualizar mesas. Apenas Superusuários e Gestores.")

        if not self.request.user.is_superuser and \
           instance.estabelecimento != self.request.user.perfil.estabelecimento:
            raise PermissionDenied("Você não tem permissão para atualizar uma mesa que não pertence ao seu estabelecimento.")

        if 'estabelecimento' in serializer.validated_data and \
           serializer.validated_data['estabelecimento'] != instance.estabelecimento:
            raise PermissionDenied("Você não tem permissão para alterar o estabelecimento de uma mesa.")
        
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado para excluir.")

        if not self._has_gestor_permission_for_write():
            raise PermissionDenied("Você não tem permissão para excluir mesas. Apenas Superusuários e Gestores.")
            
        if not self.request.user.is_superuser and \
           instance.estabelecimento != self.request.user.perfil.estabelecimento:
            raise PermissionDenied("Você não tem permissão para excluir uma mesa que não pertence ao seu estabelecimento.")
        
        instance.delete()