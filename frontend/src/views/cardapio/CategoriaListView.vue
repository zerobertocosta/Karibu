<template>
  <div class="categoria-list-container">
    <h1>Categorias do Cardápio</h1>
    <p v-if="loading">Carregando categorias...</p>
    <p v-else-if="error" class="error-message">{{ error }}</p>
    
    <div v-else-if="categorias.length > 0">
      <ul class="categoria-list">
        <li v-for="categoria in categorias" :key="categoria.id" class="categoria-item">
          <p><strong>Nome:</strong> {{ categoria.nome }}</p>
          <p><strong>Descrição:</strong> {{ categoria.descricao || 'N/A' }}</p>
          <p><strong>Ativa:</strong> {{ categoria.ativa ? 'Sim' : 'Não' }}</p>
          <p><strong>Ordem:</strong> {{ categoria.ordem }}</p>
          <p><strong>Estabelecimento:</strong> {{ categoria.estabelecimento }}</p>
          <div class="item-actions">
            <button @click="editCategoria(categoria.id)" class="btn-edit">Editar</button>
            <button @click="confirmDelete(categoria.id)" class="btn-delete">Excluir</button>
          </div>
        </li>
      </ul>
    </div>
    <p v-else>Nenhuma categoria encontrada para o seu estabelecimento.</p>

    <div class="action-buttons">
      <router-link to="/" class="btn-back">Voltar para Home</router-link>
      <button @click="addCategoria" class="btn-add">Adicionar Nova Categoria</button>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'; 

export default {
  name: 'CategoriaListView',
  data() {
    return {
      categorias: [],
      loading: true,
      error: null,
    };
  },
  async created() {
    await this.fetchCategorias();
  },
  methods: {
    async fetchCategorias() {
      this.loading = true;
      this.error = null;
      try {
        const response = await api.get('/cardapio/categorias/');
        this.categorias = response.data.results; 
      } catch (err) {
        console.error('Erro ao buscar categorias:', err);
        this.error = 'Falha ao carregar categorias. Por favor, tente novamente.';
        if (err.response && err.response.data && err.response.data.detail) {
            this.error = err.response.data.detail;
        }
      } finally {
        this.loading = false;
      }
    },
    // NOVO MÉTODO PARA ADICIONAR CATEGORIA
    addCategoria() {
      this.$router.push({ name: 'add-categoria' }); // Redireciona para a rota de adicionar
    },
    // MÉTODO PARA EDITAR CATEGORIA (futuro)
    editCategoria(id) {
      this.$router.push({ name: 'edit-categoria', params: { categoriaId: id } }); // Redireciona para a rota de editar
    },
    // MÉTODO PARA CONFIRMAR EXCLUSÃO (futuro)
    async confirmDelete(id) {
      if (confirm('Tem certeza que deseja excluir esta categoria?')) {
        try {
          await api.delete(`/cardapio/categorias/${id}/`);
          this.categorias = this.categorias.filter(cat => cat.id !== id);
          alert('Categoria excluída com sucesso!');
        } catch (err) {
          console.error('Erro ao excluir categoria:', err);
          alert('Erro ao excluir categoria: ' + (err.response?.data?.detail || ''));
        }
      }
    }
  },
};
</script>

<style scoped>
.categoria-list-container {
  padding: 30px;
  max-width: 900px;
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

.categoria-list {
  list-style: none;
  padding: 0;
  margin-top: 20px;
}

.categoria-item {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  text-align: left;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative; /* Para posicionar os botões de ação */
}

.categoria-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.categoria-item p {
  margin: 5px 0;
  color: #555;
  font-size: 1.05em;
}

.categoria-item strong {
  color: #333;
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

/* Estilos para os botões de ação (editar/excluir) */
.item-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: flex-end; /* Alinha os botões à direita */
}

.btn-edit, .btn-delete {
  padding: 8px 15px;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s ease;
}

.btn-edit {
  background-color: #ffc107; /* Amarelo */
  color: #333;
}

.btn-edit:hover {
  background-color: #e0a800;
}

.btn-delete {
  background-color: #dc3545; /* Vermelho */
  color: white;
}

.btn-delete:hover {
  background-color: #c82333;
}
</style>