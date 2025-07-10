<template>
  <div class="home">
    <h1>Bem-vindo ao Karibu!</h1>
    <p>Seu sistema de gestão para restaurantes.</p>
    <p v-if="isLoggedIn">Você está logado como: {{ username }}.</p>
    <p v-else>Faça login para acessar os recursos.</p>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      isLoggedIn: false,
      username: ''
    };
  },
  created() {
    this.checkLoginStatus();
  },
  methods: {
    checkLoginStatus() {
      this.isLoggedIn = !!localStorage.getItem('access_token');
      this.username = localStorage.getItem('username') || '';
    }
  }
};
</script>

<style scoped>
.home {
  padding: 40px;
  text-align: center;
  background-color: #f0f8ff;
  border-radius: 8px;
  margin: 30px auto;
  max-width: 800px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
h1 {
  color: #333;
  margin-bottom: 20px;
}
p {
  color: #555;
  font-size: 1.1em;
  margin-bottom: 10px;
}
</style>