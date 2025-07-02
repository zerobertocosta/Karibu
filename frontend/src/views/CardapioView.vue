<template>
  <div class="cardapio-container">
    <h1>Cardápio Karibu</h1>

    <div v-if="categorias.length">
      <div v-for="categoria in categorias" :key="categoria.id" class="categoria-section">
        <h2>{{ categoria.nome }}</h2>
        <div class="itens-grid">
          <div v-for="item in categoria.itens" :key="item.id" class="cardapio-item">
            <h3>{{ item.nome }}</h3>
            <p>{{ item.descricao }}</p>
            <p class="preco">R$ {{ parseFloat(item.preco).toFixed(2).replace('.', ',') }}</p>
            
            <div class="quantidade-selector">
              <button @click="diminuirQuantidade(item.id)" :disabled="quantidades[item.id] <= 1">-</button>
              <input type="number" v-model.number="quantidades[item.id]" min="1" @change="validarQuantidade(item.id)">
              <button @click="aumentarQuantidade(item.id)">+</button>
            </div>

            <button @click="adicionarItemAoPedido(item.id)" class="btn btn-success">
              Adicionar ao Pedido
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <p>Carregando cardápio...</p>
    </div>

    <router-link to="/" class="btn btn-secondary">Voltar para Home</router-link>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      categorias: [],
      pedidoAtual: null,
      mesaId: 1, // Assumindo mesa 1, ajuste conforme a lógica do seu app
      quantidades: {}, // Objeto para armazenar a quantidade de cada item
    };
  },
  async created() {
    await this.fetchCardapio();
    await this.fetchOrCreatePedido();
  },
  methods: {
    async fetchCardapio() {
      try {
        const response = await axios.get('http://localhost:8000/api/cardapio/categorias/');
        this.categorias = response.data;

        // Inicializa as quantidades para cada item como 1
        this.categorias.forEach(categoria => {
          categoria.itens.forEach(item => {
            // CORREÇÃO AQUI: Não precisa de this.$set no Vue 3
            this.quantidades[item.id] = 1; 
          });
        });
        console.log('Quantidades inicializadas:', this.quantidades);

      } catch (error) {
        console.error('Erro ao buscar cardápio:', error);
      }
    },
    async fetchOrCreatePedido() {
      try {
        const response = await axios.get(`http://localhost:8000/api/pedido/aberto/mesa/${this.mesaId}/`);
        this.pedidoAtual = response.data;
        console.log('Pedido existente encontrado:', this.pedidoAtual);
      } catch (error) {
        if (error.response && error.response.status === 404) {
          console.log('Nenhum pedido aberto para esta mesa. Criando um novo...');
          try {
            const createResponse = await axios.post('http://localhost:8000/api/pedido/', {
              mesa: this.mesaId,
              status: 'aberto',
              observacoes: ''
            });
            this.pedidoAtual = createResponse.data;
            console.log('Novo pedido criado:', this.pedidoAtual);
          } catch (createError) {
            console.error('Erro ao criar novo pedido:', createError);
            alert('Erro ao iniciar um novo pedido.');
          }
        } else {
          console.error('Erro ao buscar pedido:', error);
          alert('Erro ao carregar o pedido.');
        }
      }
    },
    async adicionarItemAoPedido(itemId) {
      if (!this.pedidoAtual) {
        alert('Não foi possível carregar ou criar um pedido. Tente novamente.');
        return;
      }

      const quantidade = this.quantidades[itemId] || 1;

      try {
        const response = await axios.post(`http://localhost:8000/api/pedido/${this.pedidoAtual.id}/adicionar_item/`, {
          cardapio: itemId,
          quantidade: quantidade,
        });
        this.pedidoAtual = response.data;
        alert(`${quantidade}x ${this.categorias.flatMap(c => c.itens).find(i => i.id === itemId).nome} adicionado(s) ao pedido!`);
        this.$router.push('/');
      } catch (error) {
        console.error('Erro ao adicionar item ao pedido:', error);
        alert('Erro ao adicionar item ao pedido.');
      }
    },
    // Métodos para controlar a quantidade
    diminuirQuantidade(itemId) {
      if (this.quantidades[itemId] > 1) {
        // CORREÇÃO AQUI: Não precisa de this.$set no Vue 3
        this.quantidades[itemId]--; 
      }
    },
    aumentarQuantidade(itemId) {
      // CORREÇÃO AQUI: Não precisa de this.$set no Vue 3
      this.quantidades[itemId]++; 
    },
    validarQuantidade(itemId) {
      if (this.quantidades[itemId] < 1) {
        // CORREÇÃO AQUI: Não precisa de this.$set no Vue 3
        this.quantidades[itemId] = 1;
      }
    }
  },
};
</script>

<style scoped>
.cardapio-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.categoria-section {
  margin-bottom: 30px;
}

.categoria-section h2 {
  border-bottom: 2px solid #007bff;
  padding-bottom: 5px;
  margin-bottom: 15px;
  color: #007bff;
}

.itens-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.cardapio-item {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.cardapio-item h3 {
  margin-top: 0;
  color: #333;
}

.cardapio-item p {
  color: #666;
  font-size: 0.9em;
  flex-grow: 1;
}

.cardapio-item .preco {
  font-weight: bold;
  color: #28a745;
  font-size: 1.1em;
  margin-bottom: 10px;
}

.btn {
  display: inline-block;
  padding: 8px 15px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  margin-top: 10px;
  transition: background-color 0.3s ease;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-success {
  background-color: #28a745;
  color: white;
  border: none;
}

.btn-success:hover {
  background-color: #218838;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  border: none;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* Estilos para o seletor de quantidade */
.quantidade-selector {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 10px;
}

.quantidade-selector button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.2em;
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.quantidade-selector button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.quantidade-selector input[type="number"] {
  width: 50px;
  text-align: center;
  margin: 0 5px;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  -moz-appearance: textfield;
}

/* Remove setas em Chrome/Safari/Edge */
.quantidade-selector input::-webkit-outer-spin-button,
.quantidade-selector input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>