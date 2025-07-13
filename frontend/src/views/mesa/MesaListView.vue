<template>
  <div class="mesa-list-container">
    <h1>Mesas do Estabelecimento</h1>
    <p v-if="loading">Carregando mesas...</p>
    <p v-else-if="error" class="error-message">{{ error }}</p>
    <div v-else-if="mesas.length > 0">
      <ul class="mesa-list">
        <li v-for="mesa in mesas" :key="mesa.id" class="mesa-card">
          <div class="mesa-details">
            <h3>Mesa {{ mesa.numero }}</h3>
            <p><strong>Capacidade:</strong> {{ mesa.capacidade }} pessoas</p>
            <p><strong>Status:</strong> <span :class="getStatusClass(mesa.status)">{{ getStatusDisplay(mesa.status) }}</span></p>
            <p><strong>Descrição:</strong> {{ mesa.descricao || 'N/A' }}</p>
            <p><strong>Estabelecimento:</strong> {{ mesa.estabelecimento.nome || 'N/A' }}</p>
          </div>
          <div class="mesa-actions">
            <button @click="editMesa(mesa.id)" class="btn-edit">Editar</button>
            <button @click="confirmDeleteMesa(mesa.id)" class="btn-delete">Excluir</button>
          </div>
        </li>
      </ul>
    </div>
    <p v-else>Nenhuma mesa encontrada para o seu estabelecimento.</p>
    <div class="action-buttons">
      <router-link to="/" class="btn-back">Voltar para Home</router-link>
      <button @click="addMesa" class="btn-add">Adicionar Nova Mesa</button>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'MesaListView',
  data() {
    return {
      mesas: [],
      loading: true,
      error: null,
    };
  },
  async created() {
    await this.fetchMesas();
  },
  methods: {
    async fetchMesas() {
      this.loading = true;
      this.error = null;
      try {
        const response = await api.get('/mesas/');
        this.mesas = response.data.results;
      } catch (err) {
        console.error('Erro ao buscar mesas:', err);
        this.error = 'Falha ao carregar mesas. Por favor, tente novamente.';
        if (err.response && err.response.data && err.response.data.detail) {
          this.error = err.response.data.detail;
        }
      } finally {
        this.loading = false;
      }
    },
    getStatusClass(status) {
      switch (status) {
        case 'LIVRE':
          return 'status-livre';
        case 'OCUPADA':
          return 'status-ocupada';
        case 'RESERVADA':
          return 'status-reservada';
        case 'MANUTENCAO':
          return 'status-manutencao';
        default:
          return '';
      }
    },
    getStatusDisplay(status) {
      const statusMap = {
        'LIVRE': 'Livre',
        'OCUPADA': 'Ocupada',
        'RESERVADA': 'Reservada',
        'MANUTENCAO': 'Em Manutenção',
      };
      return statusMap[status] || status;
    },
    addMesa() {
      this.$router.push({ name: 'add-mesa' });
    },
    editMesa(id) {
      this.$router.push({ name: 'edit-mesa', params: { mesaId: id } });
    },
    async confirmDeleteMesa(id) {
      if (confirm('Tem certeza que deseja excluir esta mesa?')) {
        try {
          await api.delete(`/mesas/${id}/`);
          this.mesas = this.mesas.filter(mesa => mesa.id !== id);
          alert('Mesa excluída com sucesso!');
        } catch (err) {
          console.error('Erro ao excluir mesa:', err);
          alert('Erro ao excluir mesa: ' + (err.response?.data?.detail || ''));
        }
      }
    }
  },
};
</script>

<style scoped>
.mesa-list-container {
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

.mesa-list {
  list-style: none;
  padding: 0;
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.mesa-card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  text-align: left;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.mesa-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.mesa-details h3 {
  color: #333;
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.5em;
}

.mesa-details p {
  margin: 5px 0;
  color: #555;
  font-size: 0.95em;
}

.mesa-details strong {
  color: #333;
}

/* Estilos para os status */
.status-livre {
  color: #28a745; /* Verde */
  font-weight: bold;
}

.status-ocupada {
  color: #dc3545; /* Vermelho */
  font-weight: bold;
}

.status-reservada {
  color: #ffc107; /* Amarelo/Laranja */
  font-weight: bold;
}

.status-manutencao {
  color: #6c757d; /* Cinza */
  font-weight: bold;
}

.mesa-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
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
  .mesa-list {
    grid-template-columns: 1fr;
  }
}
</style>