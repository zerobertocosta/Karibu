// frontend/src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/', // Base URL para sua API Django
  // Remova a linha abaixo para que o Content-Type seja definido automaticamente pelo FormData
  // headers: { 'Content-Type': 'application/json' }, 
});

// Interceptor para adicionar o token de acesso às requisições
api.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    // IMPORTANTE: Se a requisição contiver FormData (para upload de arquivo),
    // o navegador define automaticamente o Content-Type como 'multipart/form-data'.
    // Não precisamos defini-lo manualmente aqui, pois isso quebraria o upload.
    // Se você estiver enviando JSON, o axios já lida com isso.
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para lidar com a expiração do token e renovação
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    // Se for um erro 401 (Unauthorized) e não for uma requisição de refresh token, tenta renovar
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Marca a requisição original para evitar loops infinitos
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          // Tenta obter um novo access token usando o refresh token
          const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', { refresh: refreshToken, });
          const newAccessToken = response.data.access;
          localStorage.setItem('access_token', newAccessToken);
          // Atualiza o cabeçalho da requisição original com o novo token
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return api(originalRequest); // Repete a requisição original
        } catch (refreshError) {
          console.error('Erro ao renovar token:', refreshError);
          // Se a renovação falhar, remove os tokens e redireciona para login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('username'); // Limpar o username também
          window.location.href = '/login'; // Redireciona para a página de login
          return Promise.reject(refreshError);
        }
      } else {
        // Não há refresh token, redireciona para login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('username'); // Limpar o username também
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;