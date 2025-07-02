<!-- frontend/src/views/KitchenView.vue -->
<template>
  <div class="kitchen-view">
    <h1>Tela da Cozinha / Bar</h1>
    <p class="description">Visualize e gerencie os envios de pedidos para a cozinha/bar.</p>

    <!-- NOVO POSICIONAMENTO: Seção de Chamadas de Garçom no Topo -->
    <div class="calls-section">
      <h2>Chamadas de Garçom</h2>
      <button @click="addSimulatedCall" class="btn-action simulate-call-button">Simular Chamada da Mesa 1</button>
      <div v-if="calls.length > 0" class="calls-list">
        <div v-for="call in calls" :key="call.id" :class="['call-item', call.attended ? 'attended' : '']">
          <div class="call-details">
            <span class="call-message">Chamada da Mesa: <strong>{{ call.mesaId }}</strong></span>
            <span class="call-time">{{ formatTime(call.timestamp) }}</span>
          </div>
          <button v-if="!call.attended" @click="markCallAttended(call.id)" class="btn-action mark-attended-button">Atendido</button>
        </div>
      </div>
      <div v-else class="no-calls">
        <p>Nenhuma chamada de garçom no momento.</p>
      </div>
    </div>


    <!-- Filtros de Status (abaixo das chamadas) -->
    <div class="status-filter">
      <label for="filterStatus">Filtrar por Status:</label>
      <select id="filterStatus" v-model="filterStatus">
        <option value="">Todos (Aguardando, Em Preparo, Pronto, Entregue, Cancelado)</option>
        <option value="aguardando_envio">Aguardando Envio</option>
        <option value="em_preparo_cozinha">Em Preparo</option>
        <option value="pronto_para_entrega">Pronto para Entrega</option>
        <option value="entregue">Entregue</option>
        <option value="cancelado">Cancelado</option>
      </select>
    </div>

    <div v-if="loading" class="loading-message">
      <p>Carregando envios para a cozinha...</p>
    </div>

    <div v-if="error" class="error-message">
      <p>Erro ao carregar envios: {{ error }}</p>
    </div>

    <div v-if="filteredEnvios.length === 0 && !loading && !error" class="no-envios">
      <p>Nenhum envio com o status selecionado. Tente outro filtro ou aguarde novos pedidos!</p>
    </div>

    <div class="envios-grid">
      <div v-for="envio in filteredEnvios" :key="envio.id" class="envio-card">
        <div class="envio-header">
          <h3>Envio #{{ envio.id }} (Pedido {{ envio.pedido }})</h3>
          <span :class="['status-tag', envio.status]">{{ envio.status_display }}</span> 
        </div>
        <p class="envio-time">Enviado: {{ formatDateTime(envio.data_hora_envio) }}</p>
        <p v-if="envio.observacoes_envio" class="envio-obs">
          <strong>Obs:</strong> {{ envio.observacoes_envio }}
        </p>

        <h4>Itens Enviados:</h4>
        <ul class="envio-items-list">
          <li v-for="item in envio.itens_enviados" :key="item.id">
            <span>{{ item.quantidade }}x {{ item.cardapio.nome }}</span>
            <span>R$ {{ formatCurrency(item.subtotal) }}</span>
          </li>
        </ul>
        <p class="envio-total">Total Envio: R$ {{ formatCurrency(envio.valor_total_envio) }}</p>

        <div class="envio-actions">
          <label :for="'status-update-' + envio.id">Mudar Status:</label>
          <select 
            :id="'status-update-' + envio.id" 
            v-model="envio.status" 
            @change="updateEnvioStatus(envio.id, $event.target.value)"
          >
            <option value="aguardando_envio">Aguardando Envio</option>
            <option value="em_preparo_cozinha">Em Preparo</option>
            <option value="pronto_para_entrega">Pronto para Entrega</option>
            <option value="entregue">Entregue</option>
            <option value="cancelado">Cancelado</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- O componente do modal -->
    <AppModal ref="appModal" />
  </div>
</template>

<script>
import axios from 'axios';
import AppModal from '@/components/Modal.vue'; 

export default {
  name: 'KitchenView',
  components: {
    AppModal, 
  },
  data() {
    return {
      allEnvios: [], 
      loading: true,
      error: null,
      filterStatus: '', 
      calls: [], 
      nextCallId: 1, 
    };
  },
  computed: {
    filteredEnvios() {
      if (!this.filterStatus) {
        return this.allEnvios; 
      }
      return this.allEnvios.filter(env => env.status === this.filterStatus);
    }
  },
  async created() {
    await this.fetchKitchenEnvios();
  },
  methods: {
    formatCurrency(value) {
      const num = parseFloat(value);
      if (isNaN(num)) {
        return '0,00';
      }
      return num.toFixed(2).replace('.', ',');
    },
    formatDateTime(dateTimeString) {
      const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
      return new Date(dateTimeString).toLocaleDateString('pt-BR', options);
    },
    formatTime(dateTimeString) {
      const options = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
      return new Date(dateTimeString).toLocaleTimeString('pt-BR', options);
    },
    async showAlert(message, title = 'Aviso') {
      if (this.$refs.appModal) {
        await this.$refs.appModal.show({ title, message, type: 'alert' });
      } else {
        console.warn('AppModal não está disponível para showAlert. Usando alert nativo.', message);
        alert(`${title}: ${message}`);
      }
    },

    async fetchKitchenEnvios() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get('http://localhost:8000/api/envios_cozinha/'); 
        this.allEnvios = response.data; 
        console.log('Todos os Envios para Cozinha carregados:', this.allEnvios);
      } catch (err) {
        this.error = 'Não foi possível carregar os envios. Verifique a conexão ou o backend.';
        console.error('Erro ao buscar envios para cozinha:', err);
        await this.showAlert('Erro ao carregar envios: Verifique o console para mais detalhes.');
      } finally {
        this.loading = false;
      }
    },
    async updateEnvioStatus(envioId, newStatus) {
      try {
        console.log(`Atualizando status do envio ${envioId} para ${newStatus}...`);
        await axios.patch(`http://localhost:8000/api/envios_cozinha/${envioId}/status_envio/`, {
          status: newStatus,
        });
        console.log('Status do envio atualizado com sucesso.');
        await this.fetchKitchenEnvios(); 
        await this.showAlert(`Status do envio ${envioId} atualizado para "${newStatus}"!`);
      } catch (error) {
        console.error('Erro ao atualizar status do envio:', error);
        const errorMessage = error.response && error.response.data && error.response.data.detail 
                             ? error.response.data.detail 
                             : 'Erro desconhecido ao atualizar status do envio.';
        await this.showAlert(`Erro ao atualizar status do envio: ${errorMessage}`);
      }
    },
    addSimulatedCall() {
      const mesaId = 1; 
      this.calls.push({
        id: this.nextCallId++,
        mesaId: mesaId,
        timestamp: new Date().toISOString(),
        attended: false,
      });
      this.calls.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      this.showAlert(`Chamada simulada adicionada da Mesa ${mesaId}.`);
    },
    markCallAttended(callId) {
      const callIndex = this.calls.findIndex(call => call.id === callId);
      if (callIndex !== -1) {
        // Marcamos como atendido e filtramos para remover da lista ativa
        this.calls = this.calls.filter(call => call.id !== callId); 
        this.showAlert(`Chamada da Mesa ${this.calls[callIndex].mesaId} marcada como atendida.`);
      }
    },
  },
};
</script>

<style scoped>
/* Ajustes para compactação e responsividade */
.kitchen-view {
  padding: 15px; 
  max-width: 900px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
  line-height: 1.4; 
  color: #333;
  font-size: 0.95em; 
}

h1 {
  text-align: center;
  color: #007bff;
  margin-bottom: 8px;
  font-size: 1.6em; 
}

.description {
  text-align: center;
  color: #666;
  margin-bottom: 15px;
  font-size: 0.85em; 
}

/* NOVO: Estilos para a Seção de Chamadas de Garçom */
.calls-section {
  background-color: #f8d7da; /* Fundo vermelho claro para destaque */
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 25px; /* Adiciona espaço ABAIXO da seção */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.calls-section h2 {
  color: #721c24; 
  border-bottom: 1px solid #f5c6cb;
  padding-bottom: 8px;
  margin-bottom: 15px;
  font-size: 1.4em;
  text-align: center;
}

.calls-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 10px; 
}

.call-item {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9em;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: background-color 0.3s ease;
}

.call-item.attended {
  background-color: #d4edda; 
  color: #155724;
  border-color: #c3e6cb;
  opacity: 0.7;
}

.call-details {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.call-message {
  font-weight: bold;
  color: #333;
}

.call-message strong {
  font-size: 1.1em;
  color: #007bff;
}

.call-time {
  font-size: 0.75em;
  color: #777;
  margin-top: 3px;
}

.simulate-call-button {
  background-color: #007bff;
  color: white;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  margin-top: 10px;
  margin-bottom: 15px; /* Adiciona margem para separar do resto */
  display: block; 
  width: 100%;
  border: none;
  transition: background-color 0.3s ease;
}

.simulate-call-button:hover {
  background-color: #0056b3;
}

.mark-attended-button {
  background-color: #28a745; 
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  border: none;
  transition: background-color 0.3s ease;
  margin-left: 10px; 
  flex-shrink: 0; 
}

.mark-attended-button:hover {
  background-color: #218838;
}

.no-calls {
  text-align: center;
  color: #888;
  padding: 10px;
  font-style: italic;
}


.status-filter {
  margin-bottom: 15px;
  text-align: center;
  display: flex; 
  align-items: center;
  justify-content: center; 
  flex-wrap: wrap; 
  gap: 8px; 
}

.status-filter label {
  font-weight: bold;
  font-size: 0.9em;
}

.status-filter select {
  padding: 6px 10px;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 0.9em;
  min-width: 150px;
  max-width: 100%; 
}

.loading-message, .error-message, .no-envios {
  text-align: center;
  padding: 12px;
  border-radius: 6px;
  margin-top: 15px;
  font-size: 0.9em;
}

.envios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); 
  gap: 15px; 
  margin-top: 15px;
}

.envio-card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  padding: 12px; 
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 0.9em; 
}

.envio-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start; 
  margin-bottom: 8px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
  flex-wrap: wrap; 
  gap: 5px; 
}

.envio-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.05em; 
  flex-grow: 1; 
}

.status-tag {
  padding: 3px 6px; 
  border-radius: 12px; 
  font-size: 0.7em; 
  font-weight: bold;
  color: white;
  text-transform: uppercase;
  white-space: nowrap; 
  flex-shrink: 0; 
}

.aguardando_envio { background-color: #ffc107; color: #333; }
.em_preparo_cozinha { background-color: #17a2b8; }
.pronto_para_entrega { background-color: #28a745; }
.entregue { background-color: #6c757d; }
.cancelado { background-color: #dc3545; }

.envio-time {
  font-size: 0.8em; 
  color: #777;
  margin-bottom: 5px;
}

.envio-obs {
  background-color: #fff3cd;
  border-left: 3px solid #ffc107;
  padding: 6px 10px;
  margin-top: 8px;
  border-radius: 3px;
  font-size: 0.8em; 
  color: #856404;
}

.envio-items-list {
  list-style: none;
  padding: 0;
  margin-top: 10px;
  border-top: 1px dashed #eee;
  padding-top: 10px;
}

.envio-items-list li {
  display: flex;
  justify-content: space-between;
  padding: 3px 0;
  font-size: 0.88em; 
  border-bottom: 1px dotted #f0f0f0;
}

.envio-items-list li:last-child {
  border-bottom: none;
}

.envio-total {
  text-align: right;
  font-weight: bold;
  font-size: 0.95em; 
  color: #007bff;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 2px solid #007bff;
}

.envio-actions {
  display: flex;
  align-items: center;
  margin-top: 10px;
  gap: 8px; 
  flex-wrap: wrap; 
}

.envio-actions label {
  font-weight: bold;
  color: #555;
  flex-shrink: 0; 
  font-size: 0.85em; 
}

.envio-actions select {
  flex-grow: 1;
  padding: 5px 8px;
  border-radius: 4px;
  border: 1px solid #bbb;
  font-size: 0.85em; 
  max-width: 180px; 
}


/* Media Queries para responsividade mobile */
@media (max-width: 600px) {
  .kitchen-view {
    padding: 10px; 
    font-size: 0.9em; 
  }

  h1 {
    font-size: 1.5em;
  }
  h2 {
    font-size: 1.2em;
  }
  h3 {
    font-size: 1em;
  }

  .status-filter {
    flex-direction: column; 
    align-items: stretch; 
  }

  .status-filter select {
    max-width: 100%; 
  }

  .envios-grid, .calls-list {
    grid-template-columns: 1fr; 
  }

  .envio-card, .call-item {
    padding: 10px; 
  }

  .status-tag {
    font-size: 0.65em; 
    padding: 2px 5px;
  }

  .envio-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .envio-header h3 {
    margin-bottom: 5px;
  }

  .envio-actions {
    flex-direction: column; 
    align-items: stretch; 
  }

  .envio-actions select {
    max-width: 100%; 
  }

  .call-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .mark-attended-button {
    margin-left: 0;
    width: 100%;
  }
}
</style>
