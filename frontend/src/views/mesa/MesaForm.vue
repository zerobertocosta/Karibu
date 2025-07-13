<template>
  <div class="mesa-form-container">
    <h1>{{ isEditing ? 'Editar Mesa' : 'Adicionar Nova Mesa' }}</h1>
    <form @submit.prevent="saveMesa" class="mesa-form">
      <div class="form-group">
        <label for="numero">Número/Identificador da Mesa:</label>
        <input type="text" id="numero" v-model="mesa.numero" required class="form-control" />
      </div>
      <div class="form-group">
        <label for="capacidade">Capacidade:</label>
        <input type="number" id="capacidade" v-model.number="mesa.capacidade" required class="form-control" />
      </div>
      <div class="form-group">
        <label for="status">Status:</label>
        <select id="status" v-model="mesa.status" class="form-control">
          <option value="LIVRE">Livre</option>
          <option value="OCUPADA">Ocupada</option>
          <option value="RESERVADA">Reservada</option>
          <option value="MANUTENCAO">Em Manutenção</option>
        </select>
      </div>
      <div class="form-group">
        <label for="descricao">Descrição (Opcional):</label>
        <textarea id="descricao" v-model="mesa.descricao" class="form-control"></textarea>
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="successMessage" class="success-message">{{ successMessage }}</p>

      <div class="form-actions">
        <button type="submit" class="btn-submit" :disabled="!isGestor">{{ isEditing ? 'Salvar Alterações' : 'Adicionar Mesa' }}</button>
        <button type="button" @click="cancel" class="btn-cancel">Cancelar</button>
      </div>
    </form>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'MesaForm',
  props: {
    mesaId: {
      type: [String, Number],
      default: null,
    },
  },
  data() {
    return {
      mesa: {
        numero: '',
        capacidade: 2,
        status: 'LIVRE',
        descricao: '',
      },
      isEditing: false,
      error: null,
      successMessage: null,
    };
  },
  computed: {
    isGestor() {
      // Lê o papel do usuário do localStorage.
      // Certifique-se de que 'user_role' é o nome da chave que você está salvando no localStorage.
      return localStorage.getItem('user_role') === 'Gestor';
    }
  },
  async created() {
    if (this.mesaId) {
      this.isEditing = true;
      await this.fetchMesa(this.mesaId);
    }
    // Opcional: Se um não-gestor tentar acessar o form diretamente, redirecione.
    // Isso é uma camada extra de UX, a segurança real é no backend.
    if (!this.isGestor && (this.$route.name === 'add-mesa' || this.isEditing)) {
      this.$router.push({ name: 'mesa-list' });
      alert("Você não tem permissão para acessar o formulário de mesas.");
    }
  },
  methods: {
    async fetchMesa(id) {
      try {
        const response = await api.get(`/mesas/${id}/`);
        this.mesa = response.data;
      } catch (err) {
        console.error('Erro ao buscar mesa para edição:', err);
        this.error = 'Não foi possível carregar a mesa para edição.';
        this.successMessage = null;
      }
    },
    async saveMesa() {
      if (!this.isGestor) { // Redundância para UX, a segurança principal está no backend
          alert("Você não tem permissão para realizar esta ação.");
          return;
      }
      this.error = null;
      this.successMessage = null;
      try {
        let response;
        if (this.isEditing) {
          response = await api.patch(`/mesas/${this.mesaId}/`, this.mesa);
          this.successMessage = 'Mesa atualizada com sucesso!';
        } else {
          response = await api.post('/mesas/', this.mesa);
          this.successMessage = 'Mesa adicionada com sucesso!';
          // Limpa o formulário após adicionar
          this.mesa = { numero: '', capacidade: 2, status: 'LIVRE', descricao: '' };
        }
        console.log('Resposta da API:', response.data);
      } catch (err) {
        console.error('Erro ao salvar mesa:', err.response || err);
        this.error = 'Erro ao salvar mesa. Por favor, verifique os dados.';
        
        // --- CORREÇÃO AQUI: Tratamento de erro mais flexível ---
        if (err.response && err.response.data) {
          const errors = err.response.data;
          let errorMessage = '';

          // Itera sobre as chaves de erro
          for (const key in errors) {
            const errorValue = errors[key];
            if (Array.isArray(errorValue)) {
              // Se for um array (ex: ['Este campo é obrigatório.']), junte as mensagens
              errorMessage += `${key}: ${errorValue.join(', ')}\n`;
            } else if (typeof errorValue === 'string') {
              // Se for uma string direta (ex: "Este número de mesa já existe."), use-a
              errorMessage += `${key}: ${errorValue}\n`;
            } else if (typeof errorValue === 'object' && errorValue !== null) {
                // Para erros aninhados ou de formato complexo, tente converter para string
                errorMessage += `${key}: ${JSON.stringify(errorValue)}\n`;
            } else {
                errorMessage += `${key}: ${errorValue}\n`;
            }
          }
          // Se houver um erro 'detail' global (geralmente de permissão)
          if (errors.detail) {
              errorMessage = errors.detail;
          }

          this.error = errorMessage || this.error; // Exibe a mensagem de erro formatada
        }
        // -----------------------------------------------------------------
      }
    },
    cancel() {
      this.$router.push({ name: 'mesa-list' });
    },
  },
};
</script>

<style scoped>
/* Seu estilo CSS permanece aqui */
.mesa-form-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 60px);
  padding: 20px;
  background-color: #f4f7f6;
}

h1 {
  color: #333;
  margin-bottom: 30px;
}

.mesa-form {
  background-color: #ffffff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  text-align: left;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select,
.form-group textarea {
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.btn-submit,
.btn-cancel {
  padding: 12px 25px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-submit {
  background-color: #28a745;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background-color: #218838;
}

.btn-submit:disabled {
  background-color: #90ee90;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.error-message {
  color: #dc3545;
  margin-top: 15px;
  text-align: center;
  font-weight: bold;
}

.success-message {
  color: #28a745;
  margin-top: 15px;
  text-align: center;
  font-weight: bold;
}
</style>