<template>
  <div class="item-list-container">
    <h1>Itens do Cardápio</h1>
    <p v-if="loading">Carregando itens...</p>
    <p v-else-if="error" class="error-message">{{ error }}</p>
    <div v-else-if="itens.length > 0">
      <ul class="item-list">
        <li v-for="item in itens" :key="item.id" class="item-card" :class="{ 'item-unavailable': !item.disponivel }">
          <div class="item-details">
            <h3>{{ item.nome }}</h3>
            <p><strong>Categoria:</strong> {{ item.categoria_nome || 'N/A' }}</p>
            <p><strong>Preço:</strong> R$ {{ parseFloat(item.preco).toFixed(2) }}</p>
            <p><strong>Descrição:</strong> {{ item.descricao || 'N/A' }}</p>
            
            <p v-if="!item.disponivel" class="unavailable-tag">❌ Indisponível</p>
            <p><strong>Disponível:</strong> {{ item.disponivel ? 'Sim' : 'Não' }}</p>
            <p><strong>Ordem:</strong> {{ item.ordem }}</p>
            <p><strong>Estabelecimento:</strong> {{ item.estabelecimento_nome || 'N/A' }}</p>
            <div v-if="item.imagem" class="item-image-container">
              <img :src="item.imagem" :alt="item.nome" class="item-image" />
            </div>
            <div v-else class="item-no-image-placeholder">
              <i class="fas fa-image"></i> Sem Imagem
            </div>
          </div>
          <div class="item-actions">
            <button @click="editItem(item.id)" class="btn-edit">Editar</button>
            <button @click="confirmDeleteItem(item.id)" class="btn-delete">Excluir</button>
          </div>
        </li>
      </ul>
    </div>
    <p v-else>Nenhum item encontrado para o seu estabelecimento.</p>
    <div class="action-buttons">
      <router-link to="/" class="btn-back">Voltar para Home</router-link>
      <button @click="addItem" class="btn-add">Adicionar Novo Item</button>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
export default {
  name: 'ItemCardapioListView',
  data() {
    return {
      itens: [],
      loading: true,
      error: null,
    };
  },
  async created() {
    await this.fetchItens();
  },
  methods: {
    async fetchItens() {
      this.loading = true;
      this.error = null;
      try {
        const response = await api.get('/cardapio/itens/');
        this.itens = response.data.results;
      } catch (err) {
        console.error('Erro ao buscar itens:', err);
        this.error = 'Falha ao carregar itens do cardápio. Por favor, tente novamente.';
        if (err.response && err.response.data && err.response.data.detail) {
          this.error = err.response.data.detail;
        }
      } finally {
        this.loading = false;
      }
    },
    addItem() {
      this.$router.push({ name: 'add-item-cardapio' });
    },
    editItem(id) {
      this.$router.push({ name: 'edit-item-cardapio', params: { itemId: id } });
    },
    async confirmDeleteItem(id) {
      if (confirm('Tem certeza que deseja excluir este item do cardápio?')) {
        try {
          await api.delete(`/cardapio/itens/${id}/`);
          this.itens = this.itens.filter(item => item.id !== id);
          alert('Item excluído com sucesso!');
        } catch (err) {
          console.error('Erro ao excluir item:', err);
          alert('Erro ao excluir item: ' + (err.response?.data?.detail || ''));
        }
      }
    }
  },
};
</script>

<style scoped>
.item-list-container {
  padding: 30px;
  max-width: 1000px;
  margin: 30px auto;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h1 {
  color: #333;
  margin-bottom: 25px;
  font-size: 2.2em;
}

.item-list {
  list-style: none;
  padding: 0;
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.item-card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  text-align: left;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative; /* Para posicionar a tag de indisponível */
  overflow: hidden; /* Garante que a borda dupla fique dentro do card */
}

.item-card.item-unavailable {
  border: 2px solid #dc3545; /* Borda vermelha */
  opacity: 0.7; /* Suavemente mais opaco */
}

/* Estilo para a tag "Indisponível" */
.unavailable-tag {
  background-color: #dc3545; /* Cor de fundo vermelha */
  color: white; /* Texto branco */
  font-weight: bold;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 0.9em;
  text-align: center;
  margin: 10px 0; /* Espaçamento da tag */
  display: inline-block; /* Para ocupar apenas o espaço necessário */
}

.item-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.item-details h3 {
  color: #333;
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.5em;
}

.item-details p {
  margin: 5px 0;
  color: #555;
  font-size: 0.95em;
}

.item-details strong {
  color: #333;
}

.item-image-container {
  margin-top: 15px;
  text-align: center;
}

.item-image {
  max-width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 5px;
  border: 1px solid #eee;
}

.item-no-image-placeholder {
  margin-top: 15px;
  background-color: #e9ecef;
  color: #6c757d;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  border: 1px dashed #ced4da;
  font-size: 1.2em;
  flex-direction: column;
}

.item-no-image-placeholder i {
  font-size: 2em;
  margin-bottom: 5px;
}

.item-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn-edit,
.btn-delete {
  padding: 8px 15px;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s ease;
}

.btn-edit {
  background-color: #ffc107;
  color: #333;
}

.btn-edit:hover {
  background-color: #e0a800;
}

.btn-delete {
  background-color: #dc3545;
  color: white;
}

.btn-delete:hover {
  background-color: #c82333;
}

.error-message {
  color: #dc3545;
  font-weight: bold;
  margin-top: 20px;
}

.action-buttons {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn-back {
  background-color: #6c757d;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

.btn-back:hover {
  background-color: #5a6268;
}

.btn-add {
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-add:hover {
  background-color: #0056b3;
}

@media (max-width: 768px) {
  .item-list {
    grid-template-columns: 1fr;
  }
}
</style>