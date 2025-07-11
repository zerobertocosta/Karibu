<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link> |
      
      <template v-if="!isLoggedIn">
        <router-link to="/login">Login</router-link>
      </template>
      <template v-else>
        <button @click="logout">Sair</button>
      </template>
    </nav>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isLoggedIn: false, // Estado para controlar visibilidade do login/logout
    };
  },
  // Monitora mudanças na rota para atualizar o estado de login
  watch: {
    '$route'() {
      this.checkLoginStatus();
    }
  },
  // Verifica o status do login ao carregar o componente
  created() {
    this.checkLoginStatus();
  },
  methods: {
    checkLoginStatus() {
      this.isLoggedIn = !!localStorage.getItem('access_token');
    },
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('username'); // Limpa o username também!
      this.isLoggedIn = false;
      this.$router.push('/login'); // Redireciona para a tela de login após logout
    }
  }
}
</script>

<style>
/* Estilos globais ou para o layout principal */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  /* margin-top: 60px; */ /* Remova se não quiser o espaçamento superior */
}

nav {
  padding: 15px 30px;
  background-color: #f8f9fa; /* Um cinza claro */
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: center; /* Centraliza os links */
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* Sombra suave */
}

nav a {
  font-weight: bold;
  color: #007bff; /* Cor dos links */
  margin: 0 15px; /* Espaçamento entre os links */
  text-decoration: none;
  transition: color 0.3s ease;
}

nav a:hover {
  color: #0056b3; /* Cor dos links ao passar o mouse */
}

nav a.router-link-exact-active {
  color: #28a745; /* Cor para o link da rota ativa */
}

nav button {
  margin-left: 20px;
  padding: 8px 15px;
  background-color: #dc3545; /* Vermelho para o botão de sair */
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

nav button:hover {
  background-color: #c82333;
}
</style>