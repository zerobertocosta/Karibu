<template>
  <div class="home">
    <h1>Bem-vindo ao Karibu!</h1>
    <p>Seu sistema de gestão para restaurantes.</p>

    <div v-if="isLoggedIn" class="logged-in-content">
      <p>Você está logado como: **{{ username }}**.</p>
      
      <div class="quick-actions">
        <h2>O que você gostaria de fazer?</h2>
        <ul>
          <li>
            <router-link to="/cardapio/categorias" class="action-link">
              Gerenciar Categorias do Cardápio
            </router-link>
          </li>
          <li>
            <router-link to="/cardapio/itens" class="action-link">
              Gerenciar Itens do Cardapio
            </router-link>
          </li>
          <li>
            <router-link to="/users" class="action-link">
              Gestão de Usuários
            </router-link>
          </li>
        </ul>
      </div>
    </div>

    <div v-else class="not-logged-in-content">
      <p>Faça login para acessar os recursos do sistema.</p>
      <router-link to="/login" class="login-button">Fazer Login</router-link>
    </div>
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
    // Adiciona um listener para mudanças no localStorage, útil se o login/logout
    // acontecer em outra aba ou componente e você quiser atualizar esta visão.
    window.addEventListener('storage', this.checkLoginStatus);
  },
  beforeUnmount() {
    // Remove o listener para evitar vazamento de memória quando o componente é destruído.
    window.removeEventListener('storage', this.checkLoginStatus);
  },
  methods: {
    checkLoginStatus() {
      // Verifica se o token de acesso existe no localStorage
      this.isLoggedIn = !!localStorage.getItem('access_token');
      // Obtém o nome de usuário (se existir)
      this.username = localStorage.getItem('username') || '';
    }
  }
};
</script>

<style scoped>
.home {
  padding: 40px;
  text-align: center;
  background-color: #f0f8ff; /* Cor de fundo suave */
  border-radius: 8px;
  margin: 30px auto;
  max-width: 900px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
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

.logged-in-content {
  margin-top: 30px;
}

.quick-actions {
  margin-top: 40px;
  background-color: #fff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
}

.quick-actions h2 {
  color: #007bff; /* Azul para o título da seção */
  margin-bottom: 25px;
  font-size: 1.6em;
}

.quick-actions ul {
  list-style: none;
  padding: 0;
  display: flex;
  flex-wrap: wrap; /* Permite que os links quebrem para a próxima linha em telas menores */
  justify-content: center;
  gap: 20px; /* Espaçamento entre os links */
}

.quick-actions li {
  margin-bottom: 10px; /* Espaçamento entre os itens da lista, se eles quebrarem a linha */
}

.action-link {
  display: block; /* Ocupa a largura total do li */
  background-color: #28a745; /* Verde vibrante */
  color: white;
  padding: 15px 25px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  font-size: 1.1em;
  transition: background-color 0.3s ease, transform 0.2s ease;
  min-width: 250px; /* Garante que os botões tenham um tamanho mínimo */
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
}

.action-link:hover {
  background-color: #218838; /* Verde mais escuro no hover */
  transform: translateY(-2px); /* Efeito sutil de elevação */
}

.not-logged-in-content {
  margin-top: 30px;
}

.login-button {
  background-color: #007bff; /* Azul padrão para botão de login */
  color: white;
  padding: 12px 25px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  font-size: 1.1em;
  transition: background-color 0.3s ease;
}

.login-button:hover {
  background-color: #0056b3; /* Azul mais escuro no hover */
}
</style>