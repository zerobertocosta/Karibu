<template>
  <div class="user-management">
    <h1>Gestão de Usuários</h1>
    <p>Aqui você poderá ver, adicionar, editar e remover usuários do seu estabelecimento.</p>
    <button @click="goToAddUser">Adicionar Novo Usuário</button>

    <div v-if="users.length">
      <h2>Lista de Usuários</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome de Usuário</th>
            <th>Email</th>
            <th>Estabelecimento</th>
            <th>Função</th>
            <th>Ativo</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.perfil ? user.perfil.estabelecimento_nome : 'N/A' }}</td>
            <td>{{ user.perfil ? user.perfil.papel : 'N/A' }}</td>
            <td>{{ user.is_active ? 'Sim' : 'Não' }}</td>
            <td>
              <button @click="editUser(user.id)">Editar</button>
              <button @click="deleteUser(user.id)">Deletar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else>Nenhum usuário encontrado para este estabelecimento.</p>
  </div>
</template>

<script>
import api from '@/services/api'; // Importa a instância do Axios configurada

export default {
  name: 'UserManagementView',
  data() {
    return {
      users: [],
      loading: false,
      error: null,
    };
  },
  async created() {
    // `created` é um hook do ciclo de vida do Vue, executado quando a instância é criada.
    // Bom para buscar dados iniciais.
    this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      this.loading = true;
      this.error = null;
      try {
        // CORREÇÃO AQUI: Chamando o endpoint correto
        const response = await api.get('usuarios/users/'); 
        this.users = response.data.results; // Atribui os dados à variável users
        console.log('Usuários carregados:', this.users); // Para depuração no console
      } catch (error) {
        console.error('Erro ao buscar usuários:', error);
        this.error = 'Não foi possível carregar os usuários. Verifique sua conexão ou tente novamente.';
        // A lógica de redirecionamento para login em caso de 401/403 já está no interceptor do api.js
      } finally {
        this.loading = false;
      }
    },
    // Métodos placeholders para futuras funcionalidades
    goToAddUser() {
      this.$router.push('/users/new'); // Rota para adicionar novo usuário
    },
    editUser(userId) {
      alert('Funcionalidade de editar usuário ' + userId + ' em desenvolvimento!');
      // this.$router.push(`/users/${userId}/edit`); // Exemplo de rota para edição
    },
    deleteUser(userId) {
      alert('Funcionalidade de deletar usuário ' + userId + ' em desenvolvimento!');
      // Implementar lógica de exclusão aqui
    },
  },
};
</script>

<style scoped>
.user-management {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}
h1, h2 {
  color: #333;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}
th {
  background-color: #f2f2f2;
}
button {
  margin-right: 5px;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #007bff;
  color: white;
}
button:hover {
  opacity: 0.9;
}
button:last-child {
  margin-right: 0;
}
/* Estilos específicos para botões de deletar/editar */
button:nth-of-type(1) { /* Botão Editar */
  background-color: #ffc107;
  color: #333;
}
button:nth-of-type(2) { /* Botão Deletar */
  background-color: #dc3545;
}
</style>