// frontend/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import AboutView from '../views/AboutView.vue';
import LoginView from '../views/LoginView.vue';
import UserManagementView from '../views/UserManagementView.vue';
import UserForm from '../views/UserForm.vue';
import CategoriaListView from '../views/cardapio/CategoriaListView.vue';

// --- NOVA IMPORTAÇÃO AQUI ---
import CategoriaForm from '../views/cardapio/CategoriaForm.vue';
// --- FIM DA NOVA IMPORTAÇÃO ---

const routes = [
    {
        path: '/',
        name: 'home',
        component: HomeView,
        meta: { requiresAuth: false }
    },
    {
        path: '/about',
        name: 'about',
        component: AboutView,
        meta: { requiresAuth: false }
    },
    {
        path: '/login',
        name: 'login',
        component: LoginView,
        meta: { requiresAuth: false }
    },
    {
        path: '/users',
        name: 'user-management',
        component: UserManagementView,
        meta: { requiresAuth: true }
    },
    {
        path: '/users/add',
        name: 'add-user',
        component: UserForm,
        meta: { requiresAuth: true }
    },
    {
        path: '/users/:userId/edit',
        name: 'edit-user',
        component: UserForm,
        props: true,
        meta: { requiresAuth: true }
    },
    {
        path: '/cardapio/categorias',
        name: 'categoria-list',
        component: CategoriaListView,
        meta: { requiresAuth: true }
    },
    // --- NOVAS ROTAS AQUI ---
    {
        path: '/cardapio/categorias/add',
        name: 'add-categoria',
        component: CategoriaForm,
        meta: { requiresAuth: true }
    },
    {
        path: '/cardapio/categorias/:categoriaId/edit',
        name: 'edit-categoria',
        component: CategoriaForm,
        props: true, // Permite que o ID seja passado como prop
        meta: { requiresAuth: true }
    },
    // --- FIM DAS NOVAS ROTAS ---
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