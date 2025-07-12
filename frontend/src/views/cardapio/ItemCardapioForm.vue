<template>
  <div class="item-form-container">
    <h1>{{ isEditing ? 'Editar Item do Cardápio' : 'Adicionar Novo Item ao Cardápio' }}</h1>
    <form @submit.prevent="saveItem" class="item-form">
      
      <div class="form-group">
        <label for="nome">Nome:</label>
        <input type="text" id="nome" v-model="item.nome" required class="form-control" />
      </div>

      <div class="form-group">
        <label for="categoria">Categoria:</label>
        <select id="categoria" v-model="item.categoria_id" required class="form-control">
          <option value="">Selecione uma categoria</option>
          <option v-for="cat in categoriasDisponiveis" :key="cat.id" :value="cat.id">
            {{ cat.nome }}
          </option>
        </select>
        <p v-if="categoriasLoading">Carregando categorias...</p>
        <p v-if="categoriasError" class="error-message">{{ categoriasError }}</p>
      </div>

      <div class="form-group">
        <label for="preco">Preço:</label>
        <input type="number" id="preco" v-model.number="item.preco" step="0.01" required class="form-control" />
      </div>

      <div class="form-group">
        <label for="descricao">Descrição:</label>
        <textarea id="descricao" v-model="item.descricao" class="form-control"></textarea>
      </div>

      <div class="form-group checkbox-group">
        <input type="checkbox" id="disponivel" v-model="item.disponivel" class="form-checkbox" />
        <label for="disponivel">Disponível</label>
      </div>

      <div class="form-group">
        <label for="ordem">Ordem de Exibição:</label>
        <input type="number" id="ordem" v-model.number="item.ordem" class="form-control" />
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="successMessage" class="success-message">{{ successMessage }}</p>

      <div class="form-actions">
        <button type="submit" class="btn-submit">{{ isEditing ? 'Salvar Alterações' : 'Adicionar Item' }}</button>
        <button type="button" @click="cancel" class="btn-cancel">Cancelar</button>
      </div>
    </form>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'ItemCardapioForm',
  props: {
    itemId: {
      type: [String, Number],
      default: null,
    },
  },
  data() {
    return {
      item: {
        nome: '',
        categoria_id: '', 
        preco: 0.00,
        descricao: '',
        disponivel: true,
        ordem: 0,
        imagem: null, 
      },
      categoriasDisponiveis: [],
      categoriasLoading: true,
      categoriasError: null,
      isEditing: false,
      error: null,
      successMessage: null,
    };
  },
  async created() {
    await this.fetchCategorias();
    if (this.itemId) {
      this.isEditing = true;
      await this.fetchItem(this.itemId);
    }
  },
  methods: {
    async fetchCategorias() {
      this.categoriasLoading = true;
      this.categoriasError = null;
      try {
        const response = await api.get('/cardapio/categorias/');
        this.categoriasDisponiveis = response.data.results;
      } catch (err) {
        console.error('Erro ao buscar categorias para o formulário de item:', err);
        this.categoriasError = 'Não foi possível carregar as categorias.';
      } finally {
        this.categoriasLoading = false;
      }
    },
    async fetchItem(id) {
      try {
        const response = await api.get(`/cardapio/itens/${id}/`);
        this.item = {
          nome: response.data.nome,
          categoria_id: response.data.categoria_id, 
          preco: parseFloat(response.data.preco),
          descricao: response.data.descricao,
          disponivel: response.data.disponivel,
          ordem: response.data.ordem,
          imagem: response.data.imagem, 
        };
      } catch (err) {
        console.error('Erro ao buscar item para edição:', err);
        this.error = 'Não foi possível carregar o item para edição.';
        this.successMessage = null;
      }
    },
    async saveItem() {
      this.error = null;
      this.successMessage = null;
      try {
        let response;
        if (this.isEditing) {
          response = await api.patch(`/cardapio/itens/${this.itemId}/`, this.item);
          this.successMessage = 'Item atualizado com sucesso!';
        } else {
          response = await api.post('/cardapio/itens/', this.item);
          this.successMessage = 'Item adicionado com sucesso!';
          this.item = { nome: '', categoria_id: '', preco: 0.00, descricao: '', disponivel: true, ordem: 0, imagem: null };
        }
        console.log('Resposta da API:', response.data);
      } catch (err) {
        console.error('Erro ao salvar item:', err.response || err);
        this.error = 'Erro ao salvar item. Por favor, verifique os dados.';
        if (err.response && err.response.data) {
          const errors = err.response.data;
          let errorMessage = '';
          for (const key in errors) {
            errorMessage += `${key}: ${Array.isArray(errors[key]) ? errors[key].join(', ') : errors[key]}\n`;
          }
          this.error = errorMessage || this.error;
        }
      }
    },
    cancel() {
      this.$router.push({ name: 'item-list' });
    },
  },
};
</script>

<style scoped>
.item-form-container {
  padding: 30px;
  max-width: 700px;
  margin: 30px auto;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h1 {
  color: #333;
  margin-bottom: 25px;
  font-size: 2em;
}

.item-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  text-align: left;
}

.form-group {
  margin-bottom: 10px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
}

textarea.form-control {
  resize: vertical;
  min-height: 80px;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-checkbox {
  width: auto;
  margin-right: 5px;
}

.error-message {
  color: #dc3545;
  font-weight: bold;
  margin-top: 15px;
}

.success-message {
  color: #28a745;
  font-weight: bold;
  margin-top: 15px;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn-submit, .btn-cancel {
  padding: 12px 25px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.btn-submit:hover {
  background-color: #218838;
  transform: translateY(-2px);
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
}
</style>