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
        localStorage.setItem('username', this.username);

        // --- ATUALIZAÇÕES AQUI PARA SALVAR NOVAS INFORMAÇÕES DO PAYLOAD CUSTOMIZADO ---
        // As informações customizadas do token (role, establishment_id, is_superuser, subscription_status)
        // virão diretamente no `response.data` porque as adicionamos no `validate` do serializer.
        
        if (response.data.user_role) {
          localStorage.setItem('user_role', response.data.user_role);
        }
        if (response.data.establishment_id) {
          localStorage.setItem('establishment_id', response.data.establishment_id);
        }
        // is_superuser já é uma string "true"/"false" no localStorage
        if (typeof response.data.is_superuser !== 'undefined') {
          localStorage.setItem('is_superuser', response.data.is_superuser.toString());
        }
        if (response.data.subscription_status) { // Salva o status da assinatura
          localStorage.setItem('subscription_status', response.data.subscription_status);
        }
        // --- FIM DAS ATUALIZAÇÕES ---

        // Redireciona para a HomeView
        this.$router.push('/'); 
      } catch (err) {
        console.error('Erro no login:', err);
        // >>> Captura a mensagem de erro detalhada do backend <<<
        if (err.response && err.response.data && err.response.data.detail) {
          this.error = err.response.data.detail;
        } else if (err.response && err.response.status === 401) {
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
/* Estilos permanecem os mesmos */
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