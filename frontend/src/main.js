// frontend/src/main.js

import { createApp } from 'vue' // Importa a função createApp do Vue 3
import App from './App.vue'      // Importa o componente raiz da sua aplicação
import router from './router'    // Importa a configuração do router que você criou em './router/index.js'
import './style.css'             // ALTERADO: Importa o arquivo CSS principal, agora apontando para 'style.css'

// Cria a instância da aplicação Vue
const app = createApp(App)

// Diz à aplicação Vue para usar o router
app.use(router)

// Monta a aplicação no elemento HTML com id 'app' (geralmente em public/index.html)
app.mount('#app')