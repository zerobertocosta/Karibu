<template>
  <div class="login-container">
    <h1>Login</h1>
    <form @submit.prevent="handleLogin" class="login-form">
      <div class="form-group">
        <label for="username">Usuário:</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">Senha:</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Entrando...' : 'Entrar' }}
      </button>
      <p v-if="error" class="error-message">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import api from '@/services/api'; // Importa a instância do Axios configurada

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: null,
    };
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = null; // Limpa erros anteriores

      try {
        const response = await api.post('token/', { // Endpoint para obter o token JWT
          username: this.username,
          password: this.password,
        });

        // Armazena os tokens no localStorage
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh); // O refresh token é importante para renovar o access token

        // Redireciona o usuário para uma página protegida após o login bem-sucedido
        // Por exemplo, para a tela de gestão de usuários
        this.$router.push('/users');

      } catch (err) {
        console.error('Erro no login:', err);
        if (err.response && err.response.status === 401) {
          this.error = 'Credenciais inválidas. Verifique seu usuário e senha.';
        } else {
          this.error = 'Ocorreu um erro ao tentar fazer login. Tente novamente.';
        }
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 60px); /* Ajusta para ocupar a tela menos o nav */
  padding: 20px;
  background-color: #f4f7f6;
}

h1 {
  color: #333;
  margin-bottom: 30px;
}

.login-form {
  background-color: #ffffff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
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
.form-group input[type="password"] {
  width: calc(100% - 20px); /* Ajusta a largura considerando o padding */
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

button[type="submit"] {
  width: 100%;
  padding: 12px;
  background-color: #007bff; /* Cor primária, pode ser customizada depois */
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 18px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button[type="submit"]:hover:not(:disabled) {
  background-color: #0056b3;
}

button[type="submit"]:disabled {
  background-color: #a0cbed;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  margin-top: 15px;
  text-align: center;
  font-weight: bold;
}
</style>