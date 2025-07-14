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
import api from '@/services/api';

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
      this.error = null;
      try {
        const response = await api.post('token/', {
          username: this.username,
          password: this.password,
        });

        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        localStorage.setItem('username', this.username); // Continua salvando o username
        // Se você estiver salvando o papel do usuário (role), salve aqui também!
        // Exemplo: localStorage.setItem('user_role', response.data.user.perfil.papel);
        // Ou se o backend já retornar no payload do token


        // >>> Adicione estas linhas <<<
        // Certifique-se de que 'response.data.user.perfil.papel' e '.estabelecimento.id'
        // realmente venham na resposta do seu backend no endpoint /token/ ou em um /me/
        if (response.data.user && response.data.user.perfil) {
          localStorage.setItem('user_role', response.data.user.perfil.papel);
        if (response.data.user.perfil.estabelecimento) {
          localStorage.setItem('establishment_id', response.data.user.perfil.estabelecimento.id);
        }
        // O is_superuser pode vir diretamente no objeto user, se você o personalizar no backend
        if (typeof response.data.user.is_superuser !== 'undefined') {
          localStorage.setItem('is_superuser', response.data.user.is_superuser.toString());
        }
      }
        // >>> Fim da adição <<<

        // >>> CORREÇÃO AQUI: REDIRECIONAR PARA A HOMEPAGE APÓS LOGIN <<<
        this.$router.push('/'); // Redireciona para a HomeView
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
  min-height: calc(100vh - 60px);
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
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}
button[type="submit"] {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
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