<template>
  <div class="categoria-form-container">
    <h1>{{ isEditing ? 'Editar Categoria' : 'Adicionar Nova Categoria' }}</h1>
    <form @submit.prevent="saveCategoria" class="categoria-form">
      
      <div class="form-group">
        <label for="nome">Nome:</label>
        <input type="text" id="nome" v-model="categoria.nome" required class="form-control" />
      </div>

      <div class="form-group">
        <label for="descricao">Descrição:</label>
        <textarea id="descricao" v-model="categoria.descricao" class="form-control"></textarea>
      </div>

      <div class="form-group checkbox-group">
        <input type="checkbox" id="ativa" v-model="categoria.ativa" class="form-checkbox" />
        <label for="ativa">Ativa</label>
      </div>

      <div class="form-group">
        <label for="ordem">Ordem de Exibição:</label>
        <input type="number" id="ordem" v-model.number="categoria.ordem" class="form-control" />
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="successMessage" class="success-message">{{ successMessage }}</p>

      <div class="form-actions">
        <button type="submit" class="btn-submit">{{ isEditing ? 'Salvar Alterações' : 'Adicionar Categoria' }}</button>
        <button type="button" @click="cancel" class="btn-cancel">Cancelar</button>
      </div>
    </form>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'CategoriaForm',
  props: {
    categoriaId: { // Propriedade para receber o ID da categoria em modo de edição
      type: [String, Number],
      default: null,
    },
  },
  data() {
    return {
      categoria: {
        nome: '',
        descricao: '',
        ativa: true,
        ordem: 0,
      },
      isEditing: false,
      error: null,
      successMessage: null,
    };
  },
  async created() {
    // Verifica se estamos em modo de edição
    if (this.categoriaId) {
      this.isEditing = true;
      await this.fetchCategoria(this.categoriaId);
    }
  },
  methods: {
    async fetchCategoria(id) {
      try {
        const response = await api.get(`/cardapio/categorias/${id}/`);
        this.categoria = response.data;
      } catch (err) {
        console.error('Erro ao buscar categoria para edição:', err);
        this.error = 'Não foi possível carregar a categoria para edição.';
        this.successMessage = null;
      }
    },
    async saveCategoria() {
      this.error = null;
      this.successMessage = null;
      try {
        let response;
        if (this.isEditing) {
          // Requisição PUT/PATCH para atualizar
          response = await api.patch(`/cardapio/categorias/${this.categoriaId}/`, this.categoria);
          this.successMessage = 'Categoria atualizada com sucesso!';
        } else {
          // Requisição POST para criar
          response = await api.post('/cardapio/categorias/', this.categoria);
          this.successMessage = 'Categoria adicionada com sucesso!';
          // Limpa o formulário após adicionar, se não estiver editando
          this.categoria = { nome: '', descricao: '', ativa: true, ordem: 0 };
        }
        console.log('Resposta da API:', response.data);
      } catch (err) {
        console.error('Erro ao salvar categoria:', err.response || err);
        this.error = 'Erro ao salvar categoria. Por favor, verifique os dados.';
        if (err.response && err.response.data) {
          // Tenta exibir erros de validação do backend
          const errors = err.response.data;
          let errorMessage = '';
          for (const key in errors) {
            errorMessage += `${key}: ${errors[key].join(', ')}\n`;
          }
          this.error = errorMessage || this.error;
        }
      }
    },
    cancel() {
      this.$router.push({ name: 'categoria-list' }); // Volta para a lista de categorias
    },
  },
};
</script>

<style scoped>
.categoria-form-container {
  padding: 30px;
  max-width: 600px;
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

.categoria-form {
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
  box-sizing: border-box; /* Garante que padding não aumente a largura total */
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

.btn-submit {
  background-color: #28a745;
  color: white;
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