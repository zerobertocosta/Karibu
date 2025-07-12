<template>
  <div class="item-form-container">
    <h1>{{ isEditing ? 'Editar Item do Cardápio' : 'Adicionar Novo Item ao Cardápio' }}</h1>
    <form @submit.prevent="saveItem" class="item-form" enctype="multipart/form-data">
      <div class="form-group">
        <label for="nome">Nome:</label>
        <input type="text" id="nome" v-model="item.nome" required class="form-control" />
      </div>

      <div class="form-group">
        <label for="categoria">Categoria:</label>
        <select id="categoria" v-model="item.categoria_id" required class="form-control">
          <option :value="null" disabled>Selecione uma categoria</option>
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

      <div class="form-group">
        <label for="imagem">Imagem do Item:</label>
        <input type="file" id="imagem" @change="handleImageUpload" accept="image/*" class="form-control-file" />
        <div v-if="item.imagem_preview" class="image-preview-container">
          <img :src="item.imagem_preview" alt="Pré-visualização da Imagem" class="image-preview" />
          <button type="button" @click="removeImage" class="btn-remove-image">Remover Imagem</button>
        </div>
        <p v-else-if="item.imagem && !item.imagem_preview">
          Imagem atual: <a :href="item.imagem" target="_blank">{{ item.imagem.split('/').pop() }}</a>
          <button type="button" @click="removeImage" class="btn-remove-image">Remover Imagem</button>
        </p>
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
        <router-link to="/" class="btn-back-to-home">Voltar para Home</router-link> 
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
        categoria_id: null,
        preco: 0.00,
        descricao: '',
        disponivel: true,
        ordem: 0,
        imagem: null, // URL da imagem existente
        imagem_file: null, // Arquivo de imagem para upload
        imagem_preview: null, // URL para pré-visualização no frontend
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
          categoria_id: response.data.categoria,
          preco: parseFloat(response.data.preco),
          descricao: response.data.descricao,
          disponivel: response.data.disponivel,
          ordem: response.data.ordem,
          imagem: response.data.imagem, // URL da imagem existente
          imagem_file: null, // Sem arquivo selecionado inicialmente
          imagem_preview: response.data.imagem, // Pré-visualiza a imagem existente
        };
      } catch (err) {
        console.error('Erro ao buscar item para edição:', err);
        this.error = 'Não foi possível carregar o item para edição.';
        this.successMessage = null;
      }
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.item.imagem_file = file;
        this.item.imagem_preview = URL.createObjectURL(file); // Cria URL para pré-visualização
      } else {
        this.item.imagem_file = null;
        // Se não houver arquivo, a pré-visualização deve ser a imagem existente ou nula
        this.item.imagem_preview = this.item.imagem;
      }
    },
    removeImage() {
      this.item.imagem = null; // Remove a URL da imagem existente
      this.item.imagem_file = null; // Remove o arquivo selecionado
      this.item.imagem_preview = null; // Remove a pré-visualização
      // Opcional: Limpar o input file (útil se o usuário remover e quiser adicionar a mesma imagem novamente)
      const fileInput = this.$el.querySelector('#imagem');
      if (fileInput) fileInput.value = '';
    },
    async saveItem() {
      this.error = null;
      this.successMessage = null;
      try {
        const formData = new FormData();
        // Adiciona campos de texto/número ao FormData
        formData.append('nome', this.item.nome);
        formData.append('categoria', this.item.categoria_id); // Backend espera 'categoria', não 'categoria_id'
        formData.append('preco', this.item.preco);
        formData.append('descricao', this.item.descricao || '');
        formData.append('disponivel', this.item.disponivel);
        formData.append('ordem', this.item.ordem);
        // Adiciona a imagem ao FormData
        if (this.item.imagem_file) {
          formData.append('imagem', this.item.imagem_file);
        } else if (this.item.imagem === null && this.isEditing) {
          // Se a imagem existente foi removida e estamos editando, envie um valor vazio ou nulo
          // Para DRF, enviar uma string vazia ou 'null' pode funcionar para limpar o campo.
          // Teste com '' ou se der problema, 'null'
          formData.append('imagem', '');
        }
        let response;
        // Para requisições com FormData, o Axios e o DRF funcionam melhor com PATCH/POST.
        // O método PUT pode exigir que todos os campos sejam enviados, mesmo os não alterados.
        if (this.isEditing) {
          response = await api.patch(`/cardapio/itens/${this.itemId}/`, formData);
          this.successMessage = 'Item atualizado com sucesso!';
        } else {
          response = await api.post('/cardapio/itens/', formData);
          this.successMessage = 'Item adicionado com sucesso!';
          // Limpa o formulário após adicionar um novo item
          this.item = { nome: '', categoria_id: null, preco: 0.00, descricao: '', disponivel: true, ordem: 0, imagem: null, imagem_file: null, imagem_preview: null };
          const fileInput = this.$el.querySelector('#imagem');
          if (fileInput) fileInput.value = '';
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

.form-control-file {
  /* Novo estilo para input file */
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  background-color: #fff;
  cursor: pointer;
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

/* Estilos para pré-visualização da imagem */
.image-preview-container {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.image-preview {
  max-width: 200px;
  max-height: 200px;
  border: 1px solid #ddd;
  border-radius: 5px;
  object-fit: cover;
}

.btn-remove-image {
  background-color: #ff4d4f;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9em;
}

.btn-remove-image:hover {
  background-color: #fa3c3f;
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

.btn-submit,
.btn-cancel {
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
  padding: 12px 25px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.btn-cancel:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
}

/* NOVO ESTILO PARA O BOTÃO VOLTAR PARA HOME */
.btn-back-to-home {
  background-color: #007bff; /* Azul */
  color: white;
  padding: 12px 25px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  text-decoration: none; /* Para o router-link se comportar como botão */
  display: inline-block; /* Garante que se comporte como botão para espaçamento */
}

.btn-back-to-home:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
}
</style>