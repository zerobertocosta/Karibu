// frontend/src/services/api.js

import axios from 'axios';
import router from '@/router'; // Importe a instância do router para redirecionamento

// Crie uma instância do Axios
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
});

// Interceptor de Requisição: Adiciona o token JWT a cada requisição
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de Resposta: Lida com erros 401/403 (Não Autorizado/Proibido)
api.interceptors.response.use(
  (response) => response, // Se a resposta for sucesso, apenas passe-a
  async (error) => {
    // Se o erro for de resposta do servidor e o status for 401 ou 403
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      console.warn('Token inválido ou expirado. Redirecionando para o login.');
      // Limpa todos os tokens armazenados
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');

      // Redireciona para a página de login
      // Verifica se já não está na página de login para evitar loop de redirecionamento
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login');
      }
    }
    return Promise.reject(error); // Rejeita a promise para que o erro seja tratado nos componentes
  }
);

export default api;