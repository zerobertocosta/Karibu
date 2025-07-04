<template>
  <div class="home">
    <h1>Bem-vindo ao Karibu!</h1>
    <div v-if="mesa">
      <p>Mesa: {{ mesa.numero }}</p>
      <p>Status da Comanda: {{ mesa.disponivel ? 'Livre' : 'Ocupada' }}</p>
    </div>
    <div v-else>
      <p>Carregando informações da mesa...</p>
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

      <div class="pedido-actions" v-if="pedidoAtual && pedidoAtual.id">
        <button
          @click="confirmarFinalizarPedido"
          class="btn btn-primary finalize-button"
          :disabled="pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado'"
        >
          Finalizar Pedido (R$ {{ formatCurrency(pedidoAtual.valor_total) }})
        </button>
        <button
          v-if="pedidoAtual.status === 'fechado' || pedidoAtual.status === 'cancelado'"
          @click="confirmarNovoPedido"
          class="btn btn-success new-order-button"
        >
          Novo Pedido
        </button>
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
            </div> </div>
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

    <AppModal ref="appModal" />

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
      mesa: null, // Aqui será armazenado o objeto da mesa (ex: {id: 1, numero: 5, disponivel: true})
      pedidoAtual: null,
      cardapio: [],
      // Removido: mesaId: 1, // Este agora é obtido da rota
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
    console.log('Componente HomeView criado.');

    // 1. Obtenha o mesaId da rota
    const mesaIdFromRoute = this.$route.params.mesaId; // Acessa o ID da mesa da URL (ex: /mesa/123)

    if (mesaIdFromRoute) {
      console.log(`ID da Mesa da rota: ${mesaIdFromRoute}`);
      // 2. Chame fetchMesaInfo passando o mesaId da rota
      await this.fetchMesaInfo(mesaIdFromRoute);
    } else {
      console.warn('ID da mesa não encontrado na rota. Não foi possível buscar informações da mesa.');
      await this.showAlert('ID da mesa não encontrado na URL. Por favor, acesse via uma rota válida (ex: /mesa/1).');
      return; // Sai da função se não houver mesaId
    }

    // 3. Busque o cardápio (dependência independente do mesaId)
    await this.fetchCardapio();

    // 4. Verifique se as informações essenciais foram carregadas antes de buscar o pedido
    // Use this.mesa (a propriedade que fetchMesaInfo popula)
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
    // ---- MÉTODOS DE BUSCA E AÇÕES COM URLS CORRIGIDAS ----
    async fetchMesaInfo(mesaId) {
      try {
        console.log(`Tentando buscar informações da mesa: /api/mesas/${mesaId}/`);
        const response = await axios.get(`/api/mesas/${mesaId}/`); // CORRIGIDO: URL relativa e plural 'mesas'
        this.mesa = response.data; // Popula a propriedade 'mesa'
        console.log('Resposta da Mesa:', this.mesa);
      } catch (error) {
        console.error('Erro ao buscar informações da mesa:', error);
        this.mesa = null;
        await this.showAlert('Erro ao carregar informações da mesa. Verifique a URL ou se a mesa existe.');
      }
    },
    async fetchPedidoAtual() {
      try {
        // CORRIGIDO: Usa this.mesa.id que é o ID real da mesa carregada
        // e URL relativa para a rota personalizada
        console.log(`Tentando buscar informações do pedido para mesa: ${this.mesa.id}`);
        const response = await axios.get(`/api/pedido/aberto/mesa/${this.mesa.id}/`);
        this.pedidoAtual = response.data;
        console.log('Resposta do Pedido:', this.pedidoAtual);
      } catch (error) {
        console.error('Erro ao buscar informações do pedido:', error);
        if (error.response && error.response.status === 404) {
          console.log('Nenhum pedido aberto encontrado. Tentando criar um novo pedido...');
          try {
            // CORRIGIDO: URL relativa para a rota de criação de pedido
            const createResponse = await axios.post('/api/pedido/criar/', { // Usando a rota personalizada de criar
              mesa: this.mesa.id, // Usa o ID da mesa carregado
              status: 'aberto' // Status inicial do pedido
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
            this.pedidoAtual = null; // Only set to null if creation fails
          }
        } else {
          const errorMessage = error.response && error.response.data && error.response.data.detail
            ? error.response.data.detail
            : 'Erro desconhecido ao carregar o pedido.';
          await this.showAlert(`Erro ao carregar o pedido: ${errorMessage}`);
          this.pedidoAtual = null;
        }
      }
    },
    async fetchCardapio() {
      try {
        const response = await axios.get('/api/cardapio/'); // Já estava correto
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
        // CORRIGIDO: URL relativa
        await axios.post(`/api/pedido/${this.pedidoAtual.id}/adicionar_item/`, {
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
        // CORRIGIDO: URL relativa
        await axios.delete(`/api/pedido/${this.pedidoAtual.id}/remover_item/${itemPedidoId}/`);
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
        await this.sendToKitchen();
      }
    },

    async sendToKitchen() {
      try {
        // CORRIGIDO: URL relativa
        await axios.post(`/api/pedido/${this.pedidoAtual.id}/enviar_para_cozinha/`);
        await this.fetchPedidoAtual();
        await this.showAlert('Itens enviados para a cozinha com sucesso!');
      } catch (error) {
        console.error('Erro ao enviar para cozinha:', error);
        const errorMessage = error.response && error.response.data && error.response.data.detail
          ? error.response.data.detail
          : 'Erro desconhecido ao enviar para a cozinha.';
        await this.showAlert(`Erro ao enviar para cozinha: ${errorMessage}`);
      }
    },
    async updateEnvioStatus(envioId, newStatus) {
      try {
        // CORRIGIDO: URL relativa e endpoint correto para ViewSet (se `envios_cozinha` for um ViewSet)
        // Se este endpoint não existe e você precisa de uma função @api_view, me avise.
        // Assumo que 'envios_cozinha' é um ViewSet registrado no seu urls.py.
        await axios.patch(`/api/envios_cozinha/${envioId}/`, {
          status: newStatus
        });
        await this.showAlert('Status do envio atualizado com sucesso!');
        await this.fetchPedidoAtual();
      } catch (error) {
        console.error('Erro ao atualizar status do envio:', error);
        const errorMessage = error.response && error.response.data && error.response.data.detail
          ? error.response.data.datail
          : 'Erro desconhecido ao atualizar status do envio.';
        await this.showAlert(`Erro ao atualizar status do envio: ${errorMessage}`);
      }
    },
    async confirmarFinalizarPedido() {
      if (!this.pedidoAtual || !this.pedidoAtual.id) return;
      if (this.pedidoAtual.status === 'fechado' || this.pedidoAtual.status === 'cancelado') {
        await this.showAlert('Este pedido já está fechado ou cancelado.');
        return;
      }

      const confirmed = await this.showConfirm('Deseja realmente finalizar o pedido? Não será possível adicionar mais itens.', 'Finalizar Pedido');
      if (confirmed) {
        if (this.$refs.finalizarPedidoModal) {
          this.$refs.finalizarPedidoModal.show();
        } else {
          await this.showAlert('Componente de Finalização de Pedido não carregado.');
        }
      }
    },
    async finalizarPedido() {
      try {
        // CORRIGIDO: URL relativa
        await axios.post(`/api/pedido/${this.pedidoAtual.id}/finalizar_pedido/`);
        await this.showAlert('Pedido finalizado com sucesso!');
        await this.fetchPedidoAtual();
      } catch (error) {
        console.error('Erro ao finalizar pedido:', error);
        const errorMessage = error.response && error.response.data && error.response.data.detail
          ? error.response.data.detail
          : 'Erro desconhecido ao finalizar pedido.';
        await this.showAlert(`Erro ao finalizar pedido: ${errorMessage}`);
      }
    },
    async confirmarNovoPedido() {
      const confirmed = await this.showConfirm('Deseja realmente iniciar um novo pedido? O pedido atual será fechado (se aberto).', 'Novo Pedido');
      if (confirmed) {
        await this.criarNovoPedido();
      }
    },
    async criarNovoPedido() {
      try {
        // Não é ideal finalizar um pedido existente para criar um novo aqui,
        // o endpoint /api/pedido/criar/ já deve lidar com a criação ou retorno de um aberto.
        // Se a lógica do backend garante que apenas um pedido por mesa fica "aberto",
        // você pode remover a chamada a finalizarPedido aqui.
        // Mantenho o `this.mesa.id` pois o pedido é para a mesa atual.
        const createResponse = await axios.post('/api/pedido/criar/', { // CORRIGIDO: URL relativa para a rota de criação
          mesa: this.mesa.id, // Usa o ID da mesa carregado do data()
          status: 'aberto'
        });
        this.pedidoAtual = createResponse.data;
        this.tempCart = {}; // Clear temp cart for new order
        await this.showAlert('Um novo pedido foi iniciado!');
      } catch (createError) {
        console.error('Erro ao criar novo pedido:', createError);
        const errorMessage = createError.response && createError.response.data && createError.response.data.detail
          ? createError.response.data.detail
          : 'Erro desconhecido ao criar novo pedido.';
        await this.showAlert(`Erro ao criar novo pedido: ${errorMessage}`);
      }
    },
    async confirmarChamarGarcom() {
      if (!this.mesa || !this.mesa.id) {
        await this.showAlert('Não foi possível identificar a mesa.');
        return;
      }
      if (this.pedidoAtual && (this.pedidoAtual.status === 'fechado' || this.pedidoAtual.status === 'cancelado')) {
        await this.showAlert('Não é possível chamar o garçom para um pedido fechado ou cancelado.');
        return;
      }
      const confirmed = await this.showConfirm('Deseja realmente chamar o garçom para a mesa ' + this.mesa.numero + '?', 'Chamar Garçom');
      if (confirmed) {
        await this.chamarGarcom();
      }
    },
    async chamarGarcom() {
      try {
        // CORRIGIDO: URL relativa e plural 'mesas' no endpoint, ou sua rota personalizada
        // Se 'chamar_garcom' é uma action em MesaViewSet, `/api/mesas/${this.mesa.id}/chamar_garcom/` seria o correto.
        // Se é uma @api_view separada, o caminho estaria certo.
        await axios.post(`/api/mesa/${this.mesa.id}/chamar_garcom/`);
        await this.showAlert('Garçom chamado com sucesso!');
      } catch (error) {
        console.error('Erro ao chamar garçom:', error);
        const errorMessage = error.response && error.response.data && error.response.data.detail
          ? error.response.data.detail
          : 'Erro desconhecido ao chamar garçom.';
        await this.showAlert(`Erro ao chamar garçom: ${errorMessage}`);
      }
    },
  },
};
</script>

<style>
/* Seus estilos CSS aqui - sem alterações */

/* Estilos para .home */
.home {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
  color: #333;
}

/* Estilos para títulos */
h1, h2, h3 {
  color: #0056b3;
  margin-top: 20px;
  margin-bottom: 15px;
}

/* Estilos para informações da mesa e pedido */
div[v-if="mesa"], div[v-if="pedidoAtual"] {
  background-color: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.total-pedido-atual {
  font-size: 1.2em;
  font-weight: bold;
  color: #28a745; /* Verde para total */
  margin-top: 10px;
}

/* Estilos para itens no carrinho e envios para cozinha */
ul {
  list-style: none;
  padding: 0;
}

li {
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px 15px;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

li button {
  background-color: #dc3545; /* Vermelho para remover */
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.85em;
  transition: background-color 0.2s;
}

li button:hover:not(:disabled) {
  background-color: #c82333;
}

li button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* Estilos para botões de ação */
.btn-action, .btn-primary, .btn-success, .btn-secondary {
  background-color: #007bff; /* Azul padrão */
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  margin: 5px;
  transition: background-color 0.2s;
}

.btn-action:hover:not(:disabled), .btn-primary:hover:not(:disabled), .btn-success:hover:not(:disabled), .btn-secondary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-action:disabled, .btn-primary:disabled, .btn-success:disabled, .btn-secondary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.btn-primary { background-color: #007bff; }
.btn-primary:hover:not(:disabled) { background-color: #0056b3; }
.btn-success { background-color: #28a745; }
.btn-success:hover:not(:disabled) { background-color: #218838; }
.btn-secondary { background-color: #6c757d; }
.btn-secondary:hover:not(:disabled) { background-color: #5a6268; }

.finalize-button {
  width: auto; /* Ajusta a largura do botão */
}

.new-order-button, .call-waiter-button {
  margin-top: 10px;
  width: auto;
}

.pedido-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 20px;
}

/* Estilos para lista de envios para cozinha */
.envios-cozinha-list {
  display: grid;
  gap: 15px;
  margin-top: 15px;
}

.envio-item-cliente {
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.envio-details {
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
}

.envio-title {
  font-weight: bold;
  font-size: 1.1em;
  color: #333;
}

.envio-total-cliente {
  font-weight: bold;
  color: #28a745;
}

.envio-time-cliente {
  font-size: 0.9em;
  color: #666;
}

.status-text {
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.85em;
  color: white;
}

.status-text.aguardando_envio { background-color: #ffc107; color: #333; } /* Amarelo */
.status-text.em_preparo_cozinha { background-color: #17a2b8; } /* Azul claro */
.status-text.pronto_para_entrega { background-color: #007bff; } /* Azul */
.status-text.entregue { background-color: #28a745; } /* Verde */
.status-text.cancelado { background-color: #dc3545; } /* Vermelho */

.envio-actions-cliente {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.envio-actions-cliente label {
  font-weight: bold;
  margin-right: 5px;
}

.envio-actions-cliente select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: white;
  cursor: pointer;
  font-size: 0.9em;
}

.envio-actions-cliente select:disabled {
  background-color: #f0f0f0;
  cursor: not-allowed;
}

.cancel-button {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s;
}

.cancel-button:hover:not(:disabled) {
  background-color: #c82333;
}

.cancel-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.envio-details-dropdown {
  margin-top: 10px;
  width: 100%;
}

.envio-details-dropdown summary {
  cursor: pointer;
  font-weight: bold;
  color: #007bff;
  padding: 5px 0;
}

.envio-details-dropdown ul {
  border-top: 1px solid #eee;
  padding-top: 10px;
  margin-top: 5px;
}

.envio-details-dropdown li {
  background-color: #f9f9f9;
  border: none;
  padding: 5px 0;
  margin-bottom: 3px;
  font-size: 0.9em;
}

/* Estilos para o cardápio */
.cardapio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.cardapio-item {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  text-align: center;
}

.cardapio-item h3 {
  color: #0056b3;
  margin-top: 0;
  margin-bottom: 10px;
}

.cardapio-item p {
  color: #555;
  font-size: 0.95em;
  margin-bottom: 10px;
}

.preco-item {
  font-size: 1.1em;
  font-weight: bold;
  color: #28a745;
  margin-bottom: 15px;
}

.quantity-control {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.quantity-control button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.2s;
}

.quantity-control button:hover:not(:disabled) {
  background-color: #0056b3;
}

.quantity-control button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.quantity-control span {
  font-size: 1.1em;
  font-weight: bold;
  color: #333;
  min-width: 25px; /* Garante que o número não se mova muito */
  text-align: center;
}

/* Estilos para o carrinho temporário */
.temp-cart-summary {
  background-color: #e9f7ef; /* Verde claro */
  border: 1px solid #d4edda;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.temp-cart-summary ul {
  list-style: disc;
  padding-left: 20px;
}

.temp-cart-summary li {
  background-color: transparent;
  border: none;
  padding: 5px 0;
  margin-bottom: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.temp-cart-summary .small-button {
  background-color: #6c757d; /* Cinza */
  color: white;
  border: none;
  padding: 3px 8px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.75em;
  margin-left: 5px;
  transition: background-color 0.2s;
}

.temp-cart-summary .small-button:hover:not(:disabled) {
  background-color: #5a6268;
}

.temp-cart-total {
  font-size: 1.2em;
  font-weight: bold;
  color: #007bff; /* Azul */
  margin-top: 10px;
  text-align: right;
}

.temp-cart-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 15px;
}

.clear-cart-button {
  background-color: #ffc107; /* Amarelo */
  color: #333;
}

.clear-cart-button:hover:not(:disabled) {
  background-color: #e0a800;
}
</style>