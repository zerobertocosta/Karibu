// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/HomeView.vue';
import WaiterCallsView from '@/views/WaiterCallsView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
{
    path: '/mesa/:mesaId', // <-- ADICIONE/MODIFIQUE ESTA LINHA!
    name: 'mesaDetail',    // Nome da rota, pode ser qualquer um
    component: HomeView,   // O componente que esta rota vai carregar
    props: true            // Isso permite que 'mesaId' seja passado como prop para HomeView (mesmo não sendo usado agora, é boa prática)
  },
  // **********************************
  {
    path: '/waiter-calls',
    name: 'waiter-calls',
    component: WaiterCallsView
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE_URL),
  routes
});

export default router;
