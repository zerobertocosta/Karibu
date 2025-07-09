// frontend/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import UserManagementView from '../views/UserManagementView.vue';
import LoginView from '../views/LoginView.vue'; // <-- Importe o novo componente de Login

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'about',
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/users',
    name: 'user-management',
    component: UserManagementView
  },
  {
    path: '/login', // <-- Nova rota para a tela de login
    name: 'login',
    component: LoginView
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

// Guarda de navegação para rotas protegidas
router.beforeEach((to, from, next) => {
  const publicPages = ['/', '/about', '/login']; // <-- Adicione '/login' às rotas públicas
  const authRequired = !publicPages.includes(to.path);
  const loggedIn = localStorage.getItem('access_token');

  if (authRequired && !loggedIn) {
    // Se a rota exige autenticação e o usuário não está logado, redireciona para login
    return next('/login');
  }
  // Se o usuário está logado e tenta acessar a página de login, redireciona para a home ou users
  if (to.path === '/login' && loggedIn) {
    return next('/users'); // Ou para a dashboard principal
  }
  next(); // Permite a navegação
});


export default router;