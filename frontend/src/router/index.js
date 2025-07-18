// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import AboutView from '../views/AboutView.vue';
import LoginView from '../views/LoginView.vue';
import UserManagementView from '../views/UserManagementView.vue';
import UserForm from '../views/UserForm.vue';

import CategoriaListView from '../views/cardapio/CategoriaListView.vue';
import CategoriaForm from '../views/cardapio/CategoriaForm.vue';
import ItemCardapioListView from '../views/cardapio/ItemCardapioListView.vue';
import ItemCardapioForm from '../views/cardapio/ItemCardapioForm.vue';

// --- Importar os novos componentes de Mesa da pasta 'views/mesa' ---
import MesaListView from '../views/mesa/MesaListView.vue';
import MesaForm from '../views/mesa/MesaForm.vue';
// -----------------------------------------------------------------

const routes = [
  { path: '/', name: 'home', component: HomeView, meta: { requiresAuth: false } },
  { path: '/about', name: 'about', component: AboutView, meta: { requiresAuth: false } },
  { path: '/login', name: 'login', component: LoginView, meta: { requiresAuth: false } },

  // Rotas de Usuário
  { path: '/users', name: 'user-management', component: UserManagementView, meta: { requiresAuth: true } },
  { path: '/users/add', name: 'add-user', component: UserForm, meta: { requiresAuth: true } },
  { path: '/users/:userId/edit', name: 'edit-user', component: UserForm, props: true, meta: { requiresAuth: true } },

  // Rotas de Cardápio - Categorias
  { path: '/cardapio/categorias', name: 'categoria-list', component: CategoriaListView, meta: { requiresAuth: true } },
  { path: '/cardapio/categorias/add', name: 'add-categoria', component: CategoriaForm, meta: { requiresAuth: true } },
  { path: '/cardapio/categorias/:categoriaId/edit', name: 'edit-categoria', component: CategoriaForm, props: true, meta: { requiresAuth: true } },

  // Rotas de Cardápio - Itens
  { path: '/cardapio/itens', name: 'item-list', component: ItemCardapioListView, meta: { requiresAuth: true } },
  { path: '/cardapio/itens/add', name: 'add-item-cardapio', component: ItemCardapioForm, meta: { requiresAuth: true } },
  { path: '/cardapio/itens/:itemId/edit', name: 'edit-item-cardapio', component: ItemCardapioForm, props: true, meta: { requiresAuth: true } },

  // --- Novas Rotas de Mesa ---
  {
    path: '/mesas',
    name: 'mesa-list',
    component: MesaListView,
    meta: { requiresAuth: true }
  },
  {
    path: '/mesas/add',
    name: 'add-mesa',
    component: MesaForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/mesas/edit/:mesaId',
    name: 'edit-mesa',
    component: MesaForm,
    props: true,
    meta: { requiresAuth: true }
  },
  // -------------------------
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

router.beforeEach((to, from, next) => {
  const requiresAuth = to.meta.requiresAuth;
  const loggedIn = localStorage.getItem('access_token');

  if (requiresAuth && !loggedIn) {
    return next('/login');
  }
  if (to.path === '/login' && loggedIn) {
    return next('/');
  }
  next();
});

export default router;