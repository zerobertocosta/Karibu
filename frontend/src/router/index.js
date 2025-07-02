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
  // **** ESTE BLOCO FOI REMOVIDO ****
  // {
  //   path: '/about',
  //   name: 'about',
  //   component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  // }
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
