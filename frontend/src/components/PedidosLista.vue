<template>
  <div class="pedidos-lista">
    <h2 class="text-3xl font-semibold mb-6 text-center text-blue-700">Lista de Pedidos</h2>
    <p v-if="loading" class="text-center text-gray-600">Carregando pedidos...</p>
    <p v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">{{ error }}</p>

    <div v-if="pedidos.length > 0" class="overflow-x-auto bg-white shadow-lg rounded-lg p-4">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mesa</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pedido</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hora do Pedido</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th> </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="pedido in pedidos" :key="pedido.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ pedido.mesa_numero || pedido.mesa }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              <span class="font-semibold">{{ pedido.itens?.length || 0 }} item(s)</span>
              <span v-if="pedido.observacoes" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">OBS!</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span :class="getStatusClass(pedido.status)">{{ pedido.status }}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatarDataCurta(pedido.data_hora_pedido) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium flex items-center space-x-2">
              <select
                v-model="pedido.status"
                @change="atualizarStatusPedido(pedido.id, $event.target.value)"
                class="block w-full py-1.5 px-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option v-for="statusOpt in statusOptions" :key="statusOpt" :value="statusOpt">
                  {{ statusOpt }}
                </option>
              </select>
              <button @click="$emit('ver-detalhes', pedido.id)" class="text-indigo-600 hover:text-indigo-900 ml-2 whitespace-nowrap">Ver Detalhes</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else-if="!loading && !error" class="text-center text-gray-600 text-lg mt-8">Nenhum pedido encontrado. Crie um novo pedido no cardápio!</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PedidosLista',
  data() {
    return {
      pedidos: [],
      loading: true,
      error: null,
      // Nova propriedade de dados: opções de status
      statusOptions: ['Pendente', 'Em Preparo', 'Pronto', 'Entregue', 'Cancelado'],
    };
  },
  created() {
    this.fetchPedidos();
  },
  methods: {
    async fetchPedidos() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get('http://localhost:8000/api/pedidos/');
        this.pedidos = response.data.map(pedido => ({
          ...pedido,
          cliente_nome: pedido.cliente.nome || pedido.cliente,
          mesa_numero: pedido.mesa.numero || pedido.mesa
        }));
      } catch (err) {
        this.error = 'Erro ao carregar os pedidos. Verifique o console para mais detalhes.';
        console.error('Erro ao buscar pedidos:', err);
      } finally {
        this.loading = false;
      }
    },
    async atualizarStatusPedido(pedidoId, novoStatus) {
      try {
        await axios.patch(`http://localhost:8000/api/pedidos/${pedidoId}/`, { status: novoStatus });
        alert(`Status do pedido ${pedidoId} atualizado para "${novoStatus}"!`);
      } catch (err) {
        this.error = `Erro ao atualizar status do pedido ${pedidoId}.`;
        console.error('Erro ao atualizar status:', err.response?.data || err);
      }
    },
    formatarData(dataString) {
      if (!dataString) return 'N/A';
      const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
      return new Date(dataString).toLocaleDateString('pt-BR', options);
    },
    formatarDataCurta(dataString) {
      if (!dataString) return 'N/A';
      const date = new Date(dataString);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${day}/${month} ${hours}:${minutes}`;
    },
    getStatusClass(status) {
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
.pedidos-lista {
  padding: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
}

th {
}

tr:nth-child(even) {
}

tr:hover {
  background-color: #f1f1f1;
}

button {
  cursor: pointer;
}

select {
  min-width: 120px;
}
</style>