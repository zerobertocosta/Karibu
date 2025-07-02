<template>
  <div class="pedido-detalhes">
    <h2 class="text-3xl font-semibold mb-6 text-center text-blue-700">Detalhes do Pedido #{{ pedidoId }}</h2>
    <p v-if="loading" class="text-center text-gray-600">Carregando detalhes do pedido...</p>
    <p v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">{{ error }}</p>

    <div v-if="pedido" class="bg-white shadow-lg rounded-lg p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div><strong>Cliente:</strong> {{ pedido.cliente?.nome || pedido.cliente }}</div>
        <div><strong>Mesa:</strong> {{ pedido.mesa?.numero || pedido.mesa }}</div>
        <div><strong>Status:</strong> <span :class="getStatusClass(pedido.status)">{{ pedido.status }}</span></div>
        <div><strong>Valor Total:</strong> <span class="font-bold text-lg text-blue-600">R$ {{ parseFloat(pedido.valor_total).toFixed(2).replace('.', ',') }}</span></div>
        <div class="col-span-1 md:col-span-2"><strong>Data do Pedido:</strong> {{ formatarData(pedido.data_hora_pedido) }}</div>
        <div class="col-span-1 md:col-span-2"><strong>Observações:</strong> {{ pedido.observacoes || 'Nenhuma' }}</div>
      </div>

      <h3 class="text-2xl font-semibold mb-4 text-blue-700 border-b pb-2">Itens do Pedido:</h3>
      <ul class="divide-y divide-gray-200">
        <li v-for="item in pedido.itens" :key="item.id" class="py-3 flex justify-between items-center">
          <div class="flex-grow">
            <p class="text-lg font-medium">{{ item.quantidade }} x {{ item.produto?.nome || item.produto }}</p>
            <p class="text-gray-600 text-sm">Preço Unitário: R$ {{ parseFloat(item.preco_unitario).toFixed(2).replace('.', ',') }}</p>
          </div>
          <span class="font-semibold text-lg text-green-700">R$ {{ parseFloat(item.subtotal).toFixed(2).replace('.', ',') }}</span>
        </li>
      </ul>
    </div>
    <button @click="$emit('voltar')" class="mt-8 px-6 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition duration-300 shadow-md">Voltar à Lista</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PedidoDetalhes',
  props: ['pedidoId'], // Receberá o ID do pedido como uma prop
  data() {
    return {
      pedido: null,
      loading: true,
      error: null,
    };
  },
  // O watcher observa mudanças na prop 'pedidoId' e recarrega os detalhes
  watch: {
    pedidoId: {
      immediate: true, // Garante que a busca seja feita na primeira vez que o componente é renderizado
      handler(newId) {
        if (newId) { // Só busca se um ID válido for fornecido
          this.fetchPedidoDetalhes(newId);
        } else {
          this.pedido = null; // Limpa o pedido se o ID for nulo
          this.loading = false;
        }
      },
    },
  },
  methods: {
    async fetchPedidoDetalhes(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`http://localhost:8000/api/pedidos/${id}/`);
        // Assumimos que o backend pode retornar detalhes aninhados para cliente, mesa e produto
        this.pedido = response.data;
      } catch (err) {
        this.error = `Erro ao carregar detalhes do pedido ${id}. Verifique o console para mais detalhes.`;
        console.error(`Erro ao buscar detalhes do pedido ${id}:`, err);
        this.pedido = null; // Garante que o pedido é nulo em caso de erro
      } finally {
        this.loading = false;
      }
    },
    formatarData(dataString) {
      if (!dataString) return 'N/A';
      const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
      return new Date(dataString).toLocaleDateString('pt-BR', options);
    },
    getStatusClass(status) {
      // Classes Tailwind para estilizar o status
      switch (status) {
        case 'Pendente': return 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800';
        case 'Em Preparo': return 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800';
        case 'Pronto': return 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800';
        case 'Entregue': return 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800';
        case 'Cancelado': return 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800';
        default: return 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800';
      }
    }
  },
};
</script>

<style scoped>
.pedido-detalhes {
  padding: 20px;
  border: 1px solid #eee;
  margin-top: 20px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.pedido-detalhes h2, h3 {
  color: #333;
}
.pedido-detalhes strong {
  color: #555;
}
.pedido-detalhes ul {
  list-style-type: none;
  padding: 0;
}
.pedido-detalhes li {
  margin-bottom: 5px;
  /* background-color: #f9f9f9; */ /* Com o Tailwind, estas cores são definidas na tag, mas mantenho aqui se preferir um estilo não-Tailwind */
  /* padding: 8px; */
  /* border-radius: 4px; */
  /* border: 1px solid #eee; */
}
button {
  cursor: pointer;
}
</style>