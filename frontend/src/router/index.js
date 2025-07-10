import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import AboutView from '../views/AboutView.vue';
import LoginView from '../views/LoginView.vue';
import UserManagementView from '../views/UserManagementView.vue'; // Sua view de lista de usuários
import UserForm from '../views/UserForm.vue'; // Nova view para adicionar/editar usuários

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: false } // Home é pública
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView,
    meta: { requiresAuth: false } // About é pública
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false } // Login é pública
  },
  {
    path: '/users',
    name: 'user-management',
    component: UserManagementView,
    meta: { requiresAuth: true } // Gestão de usuários requer autenticação
  },
  {
    path: '/users/add', // Rota para adicionar novo usuário
    name: 'add-user',
    component: UserForm,
    meta: { requiresAuth: true } // Adição de usuário requer autenticação
  },
  {
    path: '/users/:userId/edit', // Rota para editar usuário existente
    name: 'edit-user',
    component: UserForm,
    props: true, // Isso permite que ':userId' seja passado como prop para UserForm
    meta: { requiresAuth: true } // Edição de usuário requer autenticação
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

// Guarda de navegação global
router.beforeEach((to, from, next) => {
  const requiresAuth = to.meta.requiresAuth; // Verifica se a rota exige autenticação
  const loggedIn = localStorage.getItem('access_token');

  if (requiresAuth && !loggedIn) {
    // Se a rota exige autenticação E o usuário não está logado, redireciona para login
    return next('/login');
  }

  if (to.path === '/login' && loggedIn) {
    // Se o usuário já está logado e tenta ir para a página de login, redireciona para /users
    return next('/users');
  }

  // Permite a navegação
  next();
});

export default router;