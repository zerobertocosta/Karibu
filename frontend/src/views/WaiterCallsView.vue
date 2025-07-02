<!-- frontend/src/views/WaiterCallsView.vue -->
<template>
  <div class="waiter-calls-container">
    <h1>Chamadas de Garçom Pendentes</h1>

    <div v-if="loading" class="loading-message">
      Carregando chamadas...
    </div>

    <div v-else-if="chamadas.length === 0" class="no-calls-message">
      Nenhuma chamada de garçom pendente no momento.
    </div>

    <div v-else class="calls-grid">
      <div v-for="chamada in chamadas" :key="chamada.id" class="call-card">
        <div class="call-header">
          <span class="call-mesa">Mesa {{ chamada.mesa.numero }}</span>
          <span class="call-time">{{ formatDateTime(chamada.data_hora_chamada) }}</span>
        </div>
        <div class="call-body">
          <p>Status: <span :class="['status-tag', chamada.status]">{{ chamada.status_display }}</span></p>
          <button 
            @click="confirmarResolverChamada(chamada.id)" 
            :disabled="chamada.status === 'resolvida'"
            class="resolve-button"
          >
            {{ chamada.status === 'resolvida' ? 'Resolvida' : 'Marcar como Resolvida' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Componente do modal de Alerta/Confirmação -->
    <AppModal ref="appModal" />
  </div>
</template>

<script>
import axios from 'axios';
import AppModal from '@/components/Modal.vue'; 

export default {
  name: 'WaiterCallsView',
  components: {
    AppModal,
  },
  data() {
    return {
      chamadas: [],
      loading: true,
    };
  },
  async created() {
    await this.fetchChamadas();
    // Opcional: Atualizar chamadas a cada X segundos para ter em tempo real
    this.interval = setInterval(this.fetchChamadas, 10000); // A cada 10 segundos
  },
  beforeUnmount() {
    clearInterval(this.interval); // Limpa o intervalo ao sair da página
  },
  methods: {
    formatDateTime(dateTimeString) {
      const options = { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit', 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
      };
      return new Date(dateTimeString).toLocaleDateString('pt-BR', options);
    },
    async showAlert(message, title = 'Aviso') {
      if (this.$refs.appModal) {
        await this.$refs.appModal.show({ title, message, type: 'alert' });
      } else {
        console.warn('AppModal não está disponível para showAlert. Usando alert nativo.', message);
        alert(`${title}: ${message}`);
      }
    },
    async showConfirm(message, title = 'Confirmar Ação') {
      if (this.$refs.appModal) {
        return await this.$refs.appModal.show({ title, message, type: 'confirm' });
      } else {
        console.warn('AppModal não está disponível para showConfirm. Usando confirm nativo.', message);
        return confirm(`${title}: ${message}`);
      }
    },
    async fetchChamadas() {
      this.loading = true;
      try {
        console.log('Buscando chamadas de garçom...');
        const response = await axios.get('http://localhost:8000/api/chamadas-garcom/');
        // Filtra para mostrar apenas as chamadas 'pendente'
        this.chamadas = response.data.filter(chamada => chamada.status === 'pendente');
        // Opcional: Ordenar por data/hora da chamada (mais recente primeiro)
        this.chamadas.sort((a, b) => new Date(b.data_hora_chamada) - new Date(a.data_hora_chamada));
        console.log('Chamadas carregadas:', this.chamadas);
      } catch (error) {
        console.error('Erro ao buscar chamadas de garçom:', error);
        const errorMessage = error.response && error.response.data && error.response.data.detail 
                             ? error.response.data.detail 
                             : 'Erro desconhecido ao carregar chamadas.';
        await this.showAlert(`Erro ao carregar chamadas: ${errorMessage}`);
      } finally {
        this.loading = false;
      }
    },
    async confirmarResolverChamada(chamadaId) {
      const confirmed = await this.showConfirm('Tem certeza que deseja marcar esta chamada como resolvida?', 'Resolver Chamada');
      if (confirmed) {
        await this.resolverChamada(chamadaId);
      }
    },
    async resolverChamada(chamadaId) {
      try {
        console.log(`Resolvendo chamada ${chamadaId}...`);
        await axios.patch(`http://localhost:8000/api/chamadas-garcom/${chamadaId}/resolver_chamada/`);
        await this.showAlert('Chamada marcada como resolvida!');
        await this.fetchChamadas(); // Atualiza a lista após resolver
      } catch (error) {
        console.error('Erro ao resolver chamada:', error);
        const errorMessage = error.response && error.response.data && error.response.data.detail 
                             ? error.response.data.detail 
                             : 'Erro desconhecido ao resolver chamada.';
        await this.showAlert(`Erro ao resolver chamada: ${errorMessage}`);
      }
    },
  },
};
</script>

<style scoped>
.waiter-calls-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
  color: #333;
}

h1 {
  text-align: center;
  color: #007bff;
  margin-bottom: 25px;
  font-size: 2em;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.loading-message, .no-calls-message {
  text-align: center;
  font-size: 1.1em;
  color: #666;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  margin-top: 30px;
}

.calls-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.call-card {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease-in-out;
}

.call-card:hover {
  transform: translateY(-5px);
}

.call-header {
  background-color: #007bff;
  color: white;
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 1.1em;
}

.call-mesa {
  font-size: 1.2em;
}

.call-time {
  font-size: 0.85em;
  opacity: 0.9;
}

.call-body {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex-grow: 1;
}

.call-body p {
  margin: 0;
  font-size: 0.95em;
  color: #555;
}

.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.8em;
  font-weight: bold;
  text-transform: uppercase;
  color: white;
}

.status-tag.pendente {
  background-color: #ffc107; /* Amarelo para pendente */
  color: #333;
}

.status-tag.resolvida {
  background-color: #28a745; /* Verde para resolvida */
}

.resolve-button {
  background-color: #28a745;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  font-weight: bold;
  transition: background-color 0.3s ease;
  margin-top: auto; /* Empurra o botão para a parte inferior do card */
}

.resolve-button:hover:not(:disabled) {
  background-color: #218838;
}

.resolve-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  opacity: 0.7;
}

@media (max-width: 768px) {
  .calls-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 480px) {
  .waiter-calls-container {
    padding: 15px;
  }
  h1 {
    font-size: 1.6em;
  }
  .calls-grid {
    grid-template-columns: 1fr; /* Uma coluna em telas muito pequenas */
  }
  .call-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  .call-time {
    font-size: 0.75em;
  }
}
</style>
