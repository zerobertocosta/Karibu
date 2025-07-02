<!-- frontend/src/views/HomeView.vue -->
<template>
  <div class="home">
    <h1>Bem-vindo ao Karibu!</h1>
    <div v-if="mesa">
      <p>Mesa: {{ mesa.numero }}</p>
      <p>Status da Comanda: {{ mesa.disponivel ? 'Livre' : 'Ocupada' }}</p>
    </div>

    <h2>Seu Pedido Atual</h2>
    <div v-if="pedidoAtual">
      <p>ID do Pedido: {{ pedidoAtual.id }}</p>
      <p>Status do Pedido: {{ pedidoAtual.status_display }}</p>
      <p class="total-pedido-atual">Valor Total: R$ {{ formatCurrency(pedidoAtual.valor_total) }}</p>

      <h3>Itens no Carrinho:</h3>
      <div v-if="pedidoAtual.itens_no_carrinho && pedidoAtual.itens_no_carrinho.length > 0">
        <ul>
          <li v-for="item in pedidoAtual.itens_no_carrinho" :key="item.id">
            <span>{{ item.cardapio.nome }} - {{ item.quantidade }}x (R$ {{ formatCurrency(item.subtotal) }})</span>
            <button 
              @click="confirmRemoveItem(item.id, item.cardapio.nome)"
              :disabled="pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado'"
            >Remover</button>
          </li>
        </ul>
        <button 
          @click="confirmSendToKitchen"
          :disabled="pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado'"
          class="btn-action"
        >Enviar para Cozinha</button>
      </div>
      <div v-else>
        <p>Nenhum item neste pedido.</p>
      </div>

      <!-- BOTÕES DE AÇÃO DO PEDIDO (Finalizar, Novo Pedido, Chamar Garçom) -->
      <div class="pedido-actions" v-if="pedidoAtual && pedidoAtual.id">
        <button 
          @click="confirmarFinalizarPedido" 
          class="btn btn-primary finalize-button"
          :disabled="pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado'"
        >
          Finalizar Pedido (R$ {{ formatCurrency(pedidoAtual.valor_total) }})
        </button>
        <!-- Botão Novo Pedido (só aparece quando o pedido atual está fechado/cancelado) -->
        <button 
          v-if="pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado'"
          @click="confirmarNovoPedido" 
          class="btn btn-success new-order-button"
        >
          Novo Pedido
        </button>
        <!-- Botão Chamar Garçom -->
        <button 
          @click="confirmarChamarGarcom" 
          class="btn btn-secondary call-waiter-button"
          :disabled="pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado'"
        >
          Chamar Garçom
        </button>
      </div>

      <h3>Envios para Cozinha:</h3>
      <div v-if="pedidoAtual.envios_cozinha && pedidoAtual.envios_cozinha.length > 0">
        <div class="envios-cozinha-list">
          <div v-for="envio in pedidoAtual.envios_cozinha" :key="envio.id" class="envio-item-cliente">
            <div class="envio-details">
                <span class="envio-title">Envio {{ envio.id }} - Status: <strong :class="['status-text', envio.status]">{{ envio.status_display }}</strong></span>
                <span class="envio-total-cliente">(R$ {{ formatCurrency(envio.valor_total_envio) }})</span>
                <span class="envio-time-cliente">Enviado: {{ formatDateTime(envio.data_hora_envio) }}</span>
            </div>
            
            <div class="envio-actions-cliente">
                <label :for="'status-update-' + envio.id">Mudar Status:</label>
                <select 
                    :id="'status-update-' + envio.id" 
                    v-model="envio.status" 
                    @change="updateEnvioStatus(envio.id, $event.target.value)"
                    :disabled="envio.status !== 'aguardando_envio' || pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado'"
                >
                    <option value="aguardando_envio">Aguardando Envio</option>
                    <option value="em_preparo_cozinha">Em Preparo</option>
                    <option value="pronto_para_entrega">Pronto para Entrega</option>
                    <option value="entregue">Entregue</option>
                    <option value="cancelado">Cancelado</option>
                </select>
                <button 
                    v-if="envio.status === 'aguardando_envio' && pedidoAtual.status !== 'fechado' && pedidoAtual.status !== 'cancelado'" 
                    @click="updateEnvioStatus(envio.id, 'cancelado')"
                    class="cancel-button"
                >
                    Cancelar Envio
                </button>
                <details class="envio-details-dropdown">
                    <summary>Ver Itens do Envio</summary>
                    <ul>
                        <li v-for="item in envio.itens_enviados" :key="item.id">
                            {{ item.quantidade }}x {{ item.cardapio.nome }} (R$ {{ formatCurrency(item.subtotal) }})
                        </li>
                    </ul>
                </details>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <p>Nenhum item enviado para a cozinha ainda.</p>
      </div>
    </div>
    <div v-else>
        <p>Carregando informações do pedido...</p>
    </div>


    <h2>Cardápio</h2>

    <!-- Seção do carrinho temporário para adicionar múltiplos itens -->
    <div class="temp-cart-summary" v-if="Object.keys(tempCart).length > 0">
      <h3>Itens a adicionar ao Pedido:</h3>
      <ul>
        <li v-for="item in tempCart" :key="item.item.id">
          {{ item.item.nome }} - {{ item.quantity }}x (R$ {{ formatCurrency(item.item.preco * item.quantity) }})
          <button @click="removeItemFromTempCart(item.item.id)" class="small-button">-</button>
          <button @click="addItemToTempCart(item.item)" class="small-button">+</button>
        </li>
      </ul>
      <p class="temp-cart-total">Total Temporário: R$ {{ formatCurrency(tempCartTotal) }}</p>
      <div class="temp-cart-actions">
        <button 
          @click="sendTempCartToPedido" 
          :disabled="pedidoAtual && (pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado')"
          class="btn-action"
        >
          Adicionar Selecionados ao Pedido
        </button>
        <button 
          @click="confirmClearTempCart" 
          class="btn-action clear-cart-button"
          :disabled="pedidoAtual && (pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado')"
        >
          Limpar Carrinho
        </button>
      </div>
    </div>
    <div v-else>
      <p>Selecione itens do cardápio abaixo para adicionar ao pedido.</p>
    </div>


    <div class="cardapio-grid">
      <div v-for="item in cardapio" :key="item.id" class="cardapio-item">
        <h3>{{ item.nome }}</h3>
        <p>{{ item.descricao }}</p>
        <p class="preco-item">R$ {{ formatCurrency(item.preco) }}</p>
        <div class="quantity-control">
          <button @click="removeItemFromTempCart(item.id)" :disabled="getTempItemQuantity(item.id) === 0 || pedidoAtual && (pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado')">-</button>
          <span>{{ getTempItemQuantity(item.id) }}</span>
          <button @click="addItemToTempCart(item)" :disabled="pedidoAtual && (pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado')">+</button>
        </div>
      </div>
    </div>
    
    <!-- Componente do modal de Alerta/Confirmação (AppModal) -->
    <AppModal ref="appModal" />

    <!-- Componente do modal de Finalizar Pedido -->
    <FinalizarPedidoModal 
      ref="finalizarPedidoModal" 
      :pedidoId="pedidoAtual ? pedidoAtual.id : null"
      :pedidoTotal="pedidoAtual ? pedidoAtual.valor_total : 0"
    />
  </div>
</template>

<script>
import axios from 'axios';
import AppModal from '@/components/Modal.vue'; 
import FinalizarPedidoModal from '@/components/FinalizarPedidoModal.vue'; 

export default {
  name: 'HomeView',
  components: {
    AppModal, 
    FinalizarPedidoModal, 
  },
  data() {
    return {
      mesa: null,
      pedidoAtual: null,
      cardapio: [],
      mesaId: 1, 
      tempCart: {}, 
    };
  },
  computed: {
    tempCartTotal() {
      return Object.values(this.tempCart).reduce((sum, cartItem) => {
        const preco = parseFloat(cartItem.item.preco);
        return sum + (isNaN(preco) ? 0 : preco * cartItem.quantity);
      }, 0);
    },
  },
  async created() {
    await this.fetchMesaInfo();
    await this.fetchCardapio();
    if (this.mesa && this.cardapio.length > 0) {
        await this.fetchPedidoAtual();
    } else {
        await this.showAlert('Não foi possível carregar as informações iniciais (mesa ou cardápio). Tente novamente.');
    }
  },
  methods: {
    formatCurrency(value) {
      const num = typeof value === 'string' ? parseFloat(value) : value;
      
      if (isNaN(num) || num === null || num === undefined) {
        return '0,00';
      }
      return parseFloat(num).toFixed(2).replace('.', ',');
    },
    formatDateTime(dateTimeString) {
      const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
      return new Date(dateTimeString).toLocaleDateString('pt-BR', options);
    },
    getTempItemQuantity(itemId) {
      return this.tempCart[itemId] ? this.tempCart[itemId].quantity : 0;
    },
    addItemToTempCart(item) {
      if (this.pedidoAtual && (this.pedidoAtual.status === 'fechado' || this.pedidoAtual.status === 'cancelado')) {
        this.showAlert('Não é possível adicionar itens a um pedido fechado ou cancelado.');
        return;
      }
      if (this.tempCart[item.id]) {
        this.tempCart[item.id].quantity++;
      } else {
        this.tempCart[item.id] = { item: item, quantity: 1 };
      }
      this.tempCart = { ...this.tempCart }; 
    },
    removeItemFromTempCart(itemId) {
      if (this.pedidoAtual && (this.pedidoAtual.status === 'fechado' || this.pedidoAtual.status === 'cancelado')) {
        this.showAlert('Não é possível remover itens de um pedido fechado ou cancelado.');
        return;
      }
      if (this.tempCart[itemId]) {
        this.tempCart[itemId].quantity--;
        if (this.tempCart[itemId].quantity <= 0) {
          delete this.tempCart[itemId];
        }
      }
      this.tempCart = { ...this.tempCart };
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

    async confirmClearTempCart() {
      if (Object.keys(this.tempCart).length === 0) {
        await this.showAlert('O carrinho temporário já está vazio!');
        return;
      }
      const confirmed = await this.showConfirm('Tem certeza que deseja limpar todos os itens do carrinho temporário?', 'Limpar Carrinho');
      if (confirmed) {
        this.tempCart = {}; 
        await this.showAlert('Carrinho temporário limpo!');
      }
    },

    async sendTempCartToPedido() {
        if (!this.pedidoAtual || !this.pedidoAtual.id) {
            await this.showAlert('Erro: Pedido não está carregado. Tente recarregar a página.');
            return;
        }
        if (this.pedidoAtual.status === 'fechado' || this.pedidoAtual.status === 'cancelado') {
            await this.showAlert('Não é possível adicionar itens a um pedido fechado ou cancelado.');
            return;
        }

        if (Object.keys(this.tempCart).length === 0) {
            await this.showAlert('Nenhum item selecionado para adicionar ao pedido.');
            return;
        }

        try {
            for (const itemId in this.tempCart) {
                const item = this.tempCart[itemId];
                console.log(`Adicionando ${item.quantity}x ${item.item.nome} ao pedido ${this.pedidoAtual.id}...`);
                await this.adicionarItemAoPedido(item.item.id, item.quantity); 
            }
            
            console.log('Itens adicionados com sucesso do carrinho temporário. Atualizando pedido...');
            await this.showAlert('Itens adicionados ao pedido!');
            this.tempCart = {}; 
            await this.fetchPedidoAtual(); 
        } catch (error) {
            console.error('Erro ao adicionar itens selecionados do cardápio:', error);
            const errorMessage = error.response && error.response.data && error.response.data.detail 
                                 ? error.response.data.detail 
                                 : 'Erro desconhecido ao adicionar itens.';
            await this.showAlert(`Erro ao adicionar itens: ${errorMessage}`);
        }
    },
    async fetchMesaInfo() {
      try {
        console.log('Tentando buscar informações da mesa...');
        const response = await axios.get(`http://localhost:8000/api/mesa/${this.mesaId}/`);
        this.mesa = response.data;
        console.log('Resposta da Mesa:', this.mesa);
      } catch (error) {
        console.error('Erro ao buscar informações da mesa:', error);
        this.mesa = null; 
      }
    },
    async fetchPedidoAtual() {
      try {
        console.log('Tentando buscar informações do pedido...');
        const response = await axios.get(`http://localhost:8000/api/pedido/aberto/mesa/${this.mesaId}/`);
        this.pedidoAtual = response.data;
        console.log('Resposta do Pedido:', this.pedidoAtual);
      } catch (error) {
        console.error('Erro ao buscar informações do pedido:', error);
        if (error.response && error.response.status === 404) {
            console.log('Nenhum pedido aberto encontrado. Tentando criar um novo pedido...');
            try {
                const createResponse = await axios.post('http://localhost:8000/api/pedido/', { 
                    mesa: this.mesaId,
                    status: 'aberto'
                });
                this.pedidoAtual = createResponse.data;
                await this.showAlert('Novo pedido criado automaticamente!'); 
                console.log('Novo pedido criado:', this.pedidoAtual);
            } catch (createError) {
                console.error('Erro ao criar novo pedido:', createError);
                const errorMessage = createError.response && createError.response.data && createError.response.data.detail 
                                     ? createError.response.data.detail 
                                     : 'Erro desconhecido ao criar novo pedido.';
                await this.showAlert(`Erro ao criar novo pedido: ${errorMessage}`);
            }
        } else {
            const errorMessage = error.response && error.response.data && error.response.data.detail 
                                 ? error.response.data.detail 
                                 : 'Erro desconhecido ao carregar o pedido.';
            await this.showAlert(`Erro ao carregar o pedido: ${errorMessage}`);
        }
        this.pedidoAtual = null; 
      }
    },
    async fetchCardapio() {
      try {
        const response = await axios.get('http://localhost:8000/api/cardapio/itens/'); 
        this.cardapio = response.data; 
        console.log('Resposta do Cardápio:', this.cardapio);
        this.cardapio.forEach(item => {
            console.log(`Item Cardápio - ID: ${item.id}, Nome: ${item.nome}, Preço: "${item.preco}", Tipo: ${typeof item.preco}`);
        });

        this.cardapio.sort((a, b) => a.nome.localeCompare(b.nome));

      } catch (error) {
        console.error('Erro ao buscar cardápio:', error);
        await this.showAlert('Erro ao buscar cardápio: Verifique a conexão com o backend.');
        this.cardapio = []; 
      }
    },
    async adicionarItemAoPedido(cardapioId, quantidade) {
        try {
            await axios.post(`http://localhost:8000/api/pedido/${this.pedidoAtual.id}/adicionar_item/`, {
                cardapio: cardapioId,
                quantidade: quantidade,
            });
        } catch (error) {
            console.error(`Erro ao adicionar item ${cardapioId} ao pedido:`, error);
            throw error; 
        }
    },
    
    async confirmRemoveItem(itemPedidoId, itemName) {
      if (!this.pedidoAtual || !this.pedidoAtual.id) return;
      if (this.pedidoAtual.status === 'fechado' || this.pedidoAtual.status === 'cancelado') {
        await this.showAlert('Não é possível remover itens de um pedido fechado ou cancelado.');
        return;
      }

      const confirmed = await this.showConfirm(`Tem certeza que deseja remover "${itemName}" do pedido?`);
      if (confirmed) {
        await this.removerItemDoPedido(itemPedidoId);
      }
    },

    async removerItemDoPedido(itemPedidoId) {
      try {
        console.log(`Removendo item ${itemPedidoId} do pedido ${this.pedidoAtual.id}...`);
        await axios.delete(`http://localhost:8000/api/pedido/${this.pedidoAtual.id}/remover_item/${itemPedidoId}/`);
        console.log('Item removido com sucesso. Atualizando pedido...');
        await this.fetchPedidoAtual(); 
        await this.showAlert('Item removido do carrinho!');
      } catch (error) {
        console.error('Erro ao remover item do pedido:', error);
        const errorMessage = error.response && error.response.data && error.response.data.detail 
                             ? error.response.data.detail 
                             : 'Erro desconhecido ao remover item.';
        await this.showAlert(`Erro ao remover item: ${errorMessage}`);
      }
    },

    async confirmSendToKitchen() {
        if (!this.pedidoAtual || !this.pedidoAtual.id || !this.pedidoAtual.itens_no_carrinho || this.pedidoAtual.itens_no_carrinho.length === 0) {
            await this.showAlert('Não há itens no carrinho para enviar.');
            return;
        }
        if (this.pedidoAtual.status === 'fechado' || this.pedidoAtual.status === 'cancelado') {
            await this.showAlert('Não é possível enviar itens para a cozinha de um pedido fechado ou cancelado.');
            return;
        }

        const confirmed = await this.showConfirm('Deseja realmente enviar os itens selecionados para a cozinha?', 'Confirmar Envio');
        if (confirmed) {
            const observacoes = prompt("Adicione observações para a cozinha (opcional):"); 
            await this.enviarItensParaCozinha(observacoes);
        }
    },

    async enviarItensParaCozinha(observacoes) {
        const itensIds = this.pedidoAtual.itens_no_carrinho.map(item => item.id);
        try {
            console.log(`Enviando itens ${itensIds} para a cozinha do pedido ${this.pedidoAtual.id}...`);
            await axios.post(`http://localhost:8000/api/pedido/${this.pedidoAtual.id}/enviar_para_cozinha/`, {
                itens_ids: itensIds,
                observacoes_envio: observacoes
            });
            console.log('Itens enviados para a cozinha com sucesso. Atualizando pedido...');
            await this.fetchPedidoAtual(); 
            await this.showAlert('Itens enviados para a cozinha!');
        } catch (error) {
            console.error('Erro ao enviar itens para a cozinha:', error);
            const errorMessage = error.response && error.response.data && error.response.data.detail 
                                 ? error.response.data.detail 
                                 : 'Erro desconhecido ao enviar itens para a cozinha.';
            await this.showAlert(`Erro ao enviar itens para a cozinha: ${errorMessage}`);
        }
    },
    async updateEnvioStatus(envioId, newStatus) {
      if (!this.pedidoAtual || !this.pedidoAtual.id) return; 
      if (this.pedidoAtual.status === 'fechado' || this.pedidoAtual.status === 'cancelado') {
        await this.showAlert('Não é possível alterar o status de um envio de um pedido fechado ou cancelado.');
        return;
      }
      
      try {
        console.log(`Atualizando status do envio ${envioId} para ${newStatus}...`);
        await axios.patch(`http://localhost:8000/api/envios_cozinha/${envioId}/status_envio/`, {
          status: newStatus,
        });
        console.log('Status do envio atualizado com sucesso.');
        await this.fetchPedidoAtual(); 
        await this.showAlert(`Status do envio ${envioId} atualizado para "${newStatus}"!`);
      } catch (error) {
        console.error('Erro ao atualizar status do envio:', error);
        const errorMessage = error.response && error.response.data && error.response.data.detail 
                             ? error.response.data.detail 
                             : 'Erro desconhecido ao atualizar status do envio.';
        await this.showAlert(`Erro ao atualizar status do envio: ${errorMessage}`);
      }
    },
    async confirmarFinalizarPedido() {
      if (!this.pedidoAtual || !this.pedidoAtual.id) {
        await this.showAlert('Não há pedido ativo para finalizar.');
        return;
      }
      if (this.pedidoAtual.status === 'fechado' || this.pedidoAtual.status === 'cancelado') {
        await this.showAlert('Pedido já está fechado ou cancelado.');
        return;
      }

      const result = await this.$refs.finalizarPedidoModal.show();

      if (result.confirmed) {
        const gorjetaValor = result.gorjeta;
        const observacoes = result.observacoes;

        try {
          console.log(`Finalizando pedido ${this.pedidoAtual.id}...`);
          const dataToSend = {
              gorjeta: gorjetaValor,
              observacoes_finalizacao: observacoes
          };
          console.log('Dados enviados na finalização:', dataToSend);

          await axios.post(`http://localhost:8000/api/pedido/${this.pedidoAtual.id}/finalizar_pedido/`, dataToSend);
          console.log('Pedido finalizado com sucesso. Atualizando informações...');
          await this.fetchPedidoAtual(); 
          await this.showAlert(`Pedido ${this.pedidoAtual.id} finalizado com sucesso!`);
        } catch (error) {
          console.error('Erro ao finalizar pedido:', error);
          const errorMessage = error.response && error.response.data && error.response.data.detail 
                               ? error.response.data.detail 
                               : 'Erro desconhecido ao finalizar pedido.';
          await this.showAlert(`Erro ao finalizar pedido: ${errorMessage}`);
        }
      } else {
          await this.showAlert('Finalização do pedido cancelada.');
      }
    },

    async confirmarNovoPedido() {
        const confirmed = await this.showConfirm('Deseja iniciar um novo pedido para esta mesa? O pedido atual será ignorado.');
        if (confirmed) {
            this.pedidoAtual = null; 
            this.tempCart = {}; 
            await this.fetchPedidoAtual(); 
        }
    },
    async confirmarChamarGarcom() {
        if (!this.pedidoAtual || !this.pedidoAtual.id) {
            await this.showAlert('Não há um pedido ativo para chamar o garçom.');
            return;
        }
        if (this.pedidoAtual.status === 'fechado' || this.pedidoAtual.status === 'cancelado') {
            await this.showAlert('Não é possível chamar o garçom para um pedido fechado ou cancelado.');
            return;
        }

        const confirmed = await this.showConfirm(`Chamar o garçom para a Mesa ${this.mesa.numero}?`, 'Chamado de Garçom');
        if (confirmed) {
            try {
                console.log(`Enviando chamada para a Mesa ${this.mesa.numero}...`);
                // Envia a requisição POST para a nova API de chamada de garçom
                await axios.post('http://localhost:8000/api/chamadas-garcom/criar-chamada/', {
                    mesa_id: this.mesa.id // Envia o ID da mesa
                });
                await this.showAlert(`Garçom chamado para a Mesa ${this.mesa.numero}! Ele estará com você em breve.`);
            } catch (error) {
                console.error('Erro ao chamar garçom:', error);
                const errorMessage = error.response && error.response.data && error.response.data.detail 
                                     ? error.response.data.detail 
                                     : 'Erro desconhecido ao chamar garçom.';
                await this.showAlert(`Erro ao chamar garçom: ${errorMessage}`);
            }
        }
    },
  },
};
</script>

<style scoped>
/* Estilos gerais do contêiner da página */
.home {
  padding: 15px; 
  max-width: 800px; 
  margin: 0 auto;
  font-family: Arial, sans-serif;
  line-height: 1.5; 
  color: #333;
  font-size: 0.95em; 
}

h1 {
  text-align: center;
  color: #007bff;
  margin-top: 15px;
  margin-bottom: 10px;
  font-size: 1.8em; 
}

h2, h3 {
  color: #333;
  margin-top: 20px;
  margin-bottom: 10px; 
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
  font-size: 1.3em; 
}

h3 {
  font-size: 1.1em; 
}


.pedido-actions {
  margin-top: 15px;
  text-align: center;
  padding: 10px 0;
  border-top: 1px solid #eee;
  display: flex; 
  justify-content: center;
  gap: 15px; 
  flex-wrap: wrap; 
}

.finalize-button {
  background-color: #007bff; 
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 1em; 
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.finalize-button:hover:not(:disabled) {
  background-color: #0056b3; 
}

.finalize-button:disabled {
  background-color: #cccccc; 
  cursor: not-allowed;
  opacity: 0.7;
}

.new-order-button {
  background-color: #28a745; 
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 1em;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.new-order-button:hover {
  background-color: #218838;
}

.call-waiter-button {
  background-color: #6c757d; 
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 1em;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.call-waiter-button:hover:not(:disabled) {
  background-color: #5a6268;
}

.call-waiter-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  opacity: 0.7;
}


.cardapio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); 
  gap: 15px; 
  margin-top: 15px;
}

.cardapio-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px; 
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  background-color: #fff;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.cardapio-item h3 {
  margin-top: 0;
  color: #555;
  border-bottom: none;
  font-size: 1em; 
}

.cardapio-item p {
  color: #666;
  font-size: 0.85em; 
  flex-grow: 1; 
}

.cardapio-item .preco-item { 
  font-weight: bold;
  color: #28a745; 
  font-size: 1em; 
  margin-top: 8px;
}

.btn-action {
  background-color: #007bff;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em; 
  margin-top: 10px;
  transition: background-color 0.3s ease;
}

.btn-action:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-action:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  opacity: 0.7;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  background-color: #f9f9f9;
  border: 1px solid #eee;
  margin-bottom: 4px; 
  padding: 6px; 
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9em; 
  flex-wrap: wrap; 
  gap: 5px;
}

li button {
  background-color: #dc3545; 
  color: white;
  padding: 4px 8px; 
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75em; 
  transition: background-color 0.3s ease;
  flex-shrink: 0; 
}

li button:hover:not(:disabled) {
  background-color: #c82333; 
}

li button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  opacity: 0.7;
}

.envios-cozinha-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
  gap: 15px; 
  margin-top: 15px;
}

.envio-item-cliente {
  background-color: #e9e9e9;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 12px; 
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.envio-details {
    display: flex;
    flex-wrap: wrap; 
    align-items: baseline;
    gap: 5px; 
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid #ddd;
}

.envio-title {
    font-weight: bold;
    font-size: 0.95em; 
    color: #333;
    flex-basis: 100%; 
    margin-bottom: 3px;
}

.status-text {
    font-size: 0.8em; 
    padding: 3px 6px;
    border-radius: 12px;
    white-space: nowrap;
    text-transform: uppercase;
    font-weight: bold;
}

.status-text.aguardando_envio { background-color: #ffc107; color: #333; }
.status-text.em_preparo_cozinha { background-color: #17a2b8; color: white;}
.status-text.pronto_para_entrega { background-color: #28a745; color: white;}
.status-text.entregue { background-color: #6c757d; color: white;}
.status-text.cancelado { background-color: #dc3545; color: white;}


.envio-total-cliente {
    font-size: 0.85em; 
    font-weight: bold;
    color: #007bff;
    flex-grow: 1; 
    text-align: right; 
}

.envio-time-cliente {
    font-size: 0.75em; 
    color: #777;
    flex-basis: 100%; 
    margin-top: 3px;
}

.envio-actions-cliente {
    display: flex;
    flex-wrap: wrap; 
    align-items: center;
    gap: 8px; 
    margin-top: 10px;
}

.envio-actions-cliente label {
    font-weight: bold;
    font-size: 0.85em; 
    flex-shrink: 0;
}

.envio-actions-cliente select {
    flex-grow: 1;
    padding: 5px 8px; 
    border-radius: 4px;
    border: 1px solid #bbb;
    font-size: 0.85em; 
    max-width: 150px; 
}

.envio-details-dropdown {
    margin-top: 10px;
    width: 100%; 
    background-color: #f2f2f2;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 0.85em; 
}

.envio-details-dropdown summary {
    cursor: pointer;
    font-weight: bold;
    color: #007bff;
}

.envio-details-dropdown details[open] summary {
    border-bottom: 1px solid #ddd;
    margin-bottom: 5px;
    padding-bottom: 5px;
}

.envio-details-dropdown ul {
    padding-left: 15px; 
    list-style: disc;
}

.envio-details-dropdown li {
    background-color: transparent;
    border: none;
    padding: 2px 0;
    font-size: 0.85em; 
}


.quantity-control {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px; 
  margin-top: 10px;
}

.quantity-control span {
  font-size: 1.1em; 
  font-weight: bold;
  min-width: 20px; 
  text-align: center;
}

.quantity-control button, .temp-cart-summary .small-button {
  background-color: #007bff;
  color: white;
  width: 28px; 
  height: 28px;
  padding: 0;
  border-radius: 50%; 
  font-size: 1.1em; 
  line-height: 1; 
  display: flex;
  align-items: center;
  justify-content: center;
}

.quantity-control button:hover:not(:disabled), .temp-cart-summary .small-button:hover:not(:disabled) {
  background-color: #0056b3;
}

.quantity-control button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  opacity: 0.7;
}

.temp-cart-summary {
  border: 1px solid #a2d2ff; 
  background-color: #e0f2ff; 
  padding: 12px; 
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  font-size: 0.9em; 
}

.temp-cart-summary h3 {
  color: #0056b3;
  border-bottom: 1px solid #b3e0ff;
  font-size: 1.05em; 
}

.temp-cart-summary ul {
  list-style: disc; 
  padding-left: 15px; 
  margin-top: 8px;
}

.temp-cart-summary li {
  background-color: transparent;
  border: none;
  margin-bottom: 2px;
  padding: 2px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9em; 
}

.temp-cart-summary .temp-cart-total { 
  font-weight: bold;
  margin-top: 10px;
  text-align: right;
  color: #0056b3;
  font-size: 0.95em; 
}

.temp-cart-actions {
  display: flex;
  flex-wrap: wrap; 
  gap: 10px; 
  margin-top: 15px;
  justify-content: flex-end; 
}

.temp-cart-actions .btn-action {
  margin-top: 0; 
  flex-grow: 1; 
  max-width: calc(50% - 5px); 
}

.temp-cart-actions .clear-cart-button {
  background-color: #dc3545; 
}

.temp-cart-actions .clear-cart-button:hover:not(:disabled) {
  background-color: #c82333;
}


.home > div:first-of-type p { 
    font-size: 0.9em;
    margin-bottom: 2px;
}

.total-pedido-atual { 
    font-weight: bold;
    font-size: 1em;
    color: #007bff;
    margin-top: 8px;
}

@media (max-width: 600px) {
  .home {
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

  .envio-details, .envio-actions-cliente {
    flex-direction: column; 
    align-items: flex-start; 
    gap: 5px;
  }

  .envio-total-cliente {
      text-align: left; 
  }

  .temp-cart-actions {
    flex-direction: column; 
    align-items: stretch;
  }

  .temp-cart-actions .btn-action {
    max-width: 100%; 
  }
}
</style>
