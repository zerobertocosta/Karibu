<template>
  <div class="mesa-form-container">
    <h1>{{ isEditing ? 'Editar Mesa' : 'Adicionar Nova Mesa' }}</h1>

    <p v-if="error" class="error-message">{{ error }}</p>
    <p v-if="successMessage" class="success-message">{{ successMessage }}</p>

    <form @submit.prevent="saveMesa" class="mesa-form">
      <div class="form-group">
        <label for="numero">Número/Identificador da Mesa:</label>
        <input type="text" id="numero" v-model="mesa.numero" required />
      </div>

      <div class="form-group">
        <label for="capacidade">Capacidade (pessoas):</label>
        <input type="number" id="capacidade" v-model.number="mesa.capacidade" required min="1" />
      </div>

      <div class="form-group">
        <label for="status">Status:</label>
        <select id="status" v-model="mesa.status" required>
          <option value="LIVRE">Livre</option>
          <option value="OCUPADA">Ocupada</option>
          <option value="RESERVADA">Reservada</option>
          <option value="MANUTENCAO">Em Manutenção</option>
        </select>
      </div>

      <div class="form-group">
        <label for="descricao">Descrição (opcional):</label>
        <textarea id="descricao" v-model="mesa.descricao"></textarea>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-save">{{ isEditing ? 'Salvar Alterações' : 'Adicionar Mesa' }}</button>
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
      const role = localStorage.getItem('user_role');
      const isSuperuser = localStorage.getItem('is_superuser') === 'true'; // Assume 'is_superuser' é salvo como string
      // Um superusuário também pode gerenciar, então incluímos ele aqui
      return isSuperuser || role === 'gestor';
    }
  },
  async created() {
    // >>> Reintroduzindo e ajustando a verificação de permissão no frontend <<<
    // Redireciona se não for gestor/superuser e tentar acessar o formulário diretamente
    if (!this.isGestor) {
      alert("Você não tem permissão para acessar o formulário de gestão de mesas.");
      this.$router.push({ name: 'mesa-list' });
      return; // Importante para parar a execução do created()
    }
    // >>> Fim da verificação de permissão <<<

    if (this.mesaId) {
      this.isEditing = true;
      await this.fetchMesa(this.mesaId);
    }
  },
  methods: {
    async fetchMesa(id) {
      try {
        const response = await api.get(`/mesas/${id}/`);
        this.mesa = response.data;
      } catch (error) {
        console.error("Erro ao buscar mesa para edição:", error);
        this.error = "Erro ao carregar dados da mesa para edição.";
        // Se houver um erro 404 (não encontrado) ou 403 (proibido), redirecionar
        if (error.response && (error.response.status === 404 || error.response.status === 403)) {
          this.error = error.response.data.detail || "Mesa não encontrada ou você não tem permissão.";
          this.$router.push({ name: 'mesa-list' });
        }
      }
    },
    async saveMesa() {
      if (!this.isGestor) { // Verificação redundante, mas boa para evitar envio
        alert("Você não tem permissão para realizar esta ação.");
        return;
      }
      this.error = null;
      this.successMessage = null;
      try {
        let response;
        if (this.isEditing) {
          response = await api.put(`/mesas/${this.mesaId}/`, this.mesa);
          this.successMessage = 'Mesa atualizada com sucesso!';
        } else {
          response = await api.post('/mesas/', this.mesa);
          this.successMessage = 'Mesa cadastrada com sucesso!';
        }
        console.log('Resposta da API:', response.data);
        // Após salvar, redireciona para a lista
        this.$router.push({ name: 'mesa-list' });
      } catch (err) {
        console.error('Erro ao salvar mesa:', err.response ? err.response.data : err.message);
        this.error = 'Erro ao salvar mesa. Verifique os dados.';
        if (err.response && err.response.data) {
          if (err.response.data.detail) {
            this.error = err.response.data.detail;
          } else {
            // Concatena mensagens de erro de validação (ex: campo 'numero' já existe)
            this.error = Object.values(err.response.data).flat().join('; ');
          }
        }
      }
    },
    cancel() {
      this.$router.push({ name: 'mesa-list' });
    }
  },
};
</script>

<style scoped>
.mesa-form-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h1 {
  color: #333;
  margin-bottom: 30px;
  font-size: 2em;
}

.mesa-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: bold;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box; /* Garante que padding não aumente a largura */
  font-size: 1em;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
}

.form-group textarea {
  resize: vertical; /* Permite redimensionar verticalmente */
  min-height: 80px;
}

.form-actions {
  margin-top: 25px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn-save,
.btn-cancel {
  padding: 12px 25px;
  border: none;
  border-radius: 5px;
  font-size: 1em;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-save {
  background-color: #28a745;
  color: white;
}

.btn-save:hover {
  background-color: #218838;
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
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.success-message {
  color: #28a745;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 20px;
}
</style>