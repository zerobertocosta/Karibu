<template>
  <div class="user-management">
    <h1>Gestão de Usuários</h1>

    <div class="actions">
      <button @click="navigateToAddUser" class="add-user-button">Adicionar Novo Usuário</button>
    </div>

    <div v-if="loading" class="loading">Carregando usuários...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <table v-if="users.length && !loading">
      <thead>
        <tr>
          <th>ID</th>
          <th>Usuário</th>
          <th>Email</th>
          <th>Papel</th>
          <th>Estabelecimento</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.perfil ? user.perfil.papel : 'N/A' }}</td>
          <td>{{ user.perfil && user.perfil.estabelecimento ? user.perfil.estabelecimento.nome : 'N/A' }}</td>
          <td>
            <button @click="editUser(user.id)" class="edit-button">Editar</button>
            <button @click="deleteUser(user.id)" class="delete-button">Excluir</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else-if="!loading && !error">Nenhum usuário encontrado ou você não tem permissão para visualizar.</p>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'UserManagementView',
  data() {
    return {
      users: [],
      loading: false,
      error: null,
      isSuperuser: false, // Adicionar para determinar se o usuário logado é superuser
      loggedInUserEstablishmentId: null, // ID do estabelecimento do gestor logado
    };
  },
  async created() {
    await this.fetchLoggedInUserContext(); // Busca o contexto do usuário logado primeiro
    this.fetchUsers(); // Em seguida, busca os usuários
  },
  methods: {
    async fetchLoggedInUserContext() {
      try {
        const username = localStorage.getItem('username');
        if (!username) {
            console.warn("Nome de usuário não encontrado no localStorage. Não foi possível determinar o contexto do gestor.");
            this.error = "Por favor, faça login novamente para gerenciar usuários.";
            this.$router.push('/login');
            return;
        }

        const response = await api.get(`usuarios/users/?username=${username}`); 
        const currentUser = response.data.results[0]; // Assume que o primeiro resultado é o correto

        if (currentUser) {
          this.isSuperuser = currentUser.is_superuser;
          if (currentUser.perfil && currentUser.perfil.estabelecimento) {
            this.loggedInUserEstablishmentId = currentUser.perfil.estabelecimento.id; 
          }
        } else {
          console.warn("Usuário logado não encontrado na resposta da API.");
          this.error = "Não foi possível carregar o perfil do usuário logado.";
        }
      } catch (error) {
        console.error('Erro ao carregar contexto do usuário logado:', error);
        this.error = 'Não foi possível carregar as informações do gestor.';
      }
    },
    async fetchUsers() {
      this.loading = true;
      this.error = null;
      try {
        let url = 'usuarios/users/';
        // Se não for superusuário, filtra pela empresa do gestor
        if (!this.isSuperuser && this.loggedInUserEstablishmentId) {
          url += `?perfil__estabelecimento__id=${this.loggedInUserEstablishmentId}`;
        }
        
        const response = await api.get(url);
        this.users = response.data.results;
      } catch (error) {
        console.error('Erro ao carregar usuários:', error.response ? error.response.data : error.message);
        this.error = 'Não foi possível carregar os usuários.';
        if (error.response && error.response.status === 403) {
            this.error = 'Você não tem permissão para visualizar esta lista.';
        } else if (error.response && error.response.status === 401) {
            this.$router.push('/login'); // Redireciona para login se não autenticado
        }
      } finally {
        this.loading = false;
      }
    },
    navigateToAddUser() {
      this.$router.push('/users/add');
    },
    editUser(userId) {
      this.$router.push({ name: 'edit-user', params: { userId: userId } });
    },
    async deleteUser(userId) {
      if (confirm('Tem certeza que deseja excluir este usuário?')) {
        this.loading = true;
        this.error = null;
        try {
          await api.delete(`usuarios/users/${userId}/`);
          this.users = this.users.filter(user => user.id !== userId); // Remove da lista
          alert('Usuário excluído com sucesso!');
        } catch (error) {
          console.error('Erro ao excluir usuário:', error.response ? error.response.data : error.message);
          this.error = 'Não foi possível excluir o usuário.';
        } finally {
          this.loading = false;
        }
      }
    }
  },
};
</script>

<style scoped>
.user-management {
  padding: 20px;
  max-width: 1000px;
  margin: 20px auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h1 {
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.actions {
  text-align: right;
  margin-bottom: 20px;
}

.add-user-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.add-user-button:hover {
  background-color: #0056b3;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
  font-weight: bold;
  color: #333;
}

tr:nth-child(even) {
  background-color: #f9f9f9;
}

.edit-button, .delete-button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 5px;
}

.edit-button {
  background-color: #ffc107;
  color: #333;
}

.edit-button:hover {
  background-color: #e0a800;
}

.delete-button {
  background-color: #dc3545;
  color: white;
}

.delete-button:hover {
  background-color: #c82333;
}

.loading, .error {
  text-align: center;
  margin-top: 20px;
  font-weight: bold;
}

.loading {
  color: #007bff;
}

.error {
  color: #dc3545;
}
</style>