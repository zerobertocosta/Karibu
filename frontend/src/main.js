import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store'; // Mantenha se você usa Vuex/Pinia, caso contrário pode remover esta linha

createApp(App)
  .use(store) // Mantenha se você usa store, caso contrário remova esta linha
  .use(router)
  .mount('#app');