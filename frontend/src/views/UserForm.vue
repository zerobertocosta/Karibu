<template>
  <div class="user-form-container">
    <h1>{{ isEditMode ? 'Editar Usuário' : 'Adicionar Novo Usuário' }}</h1>

    <form @submit.prevent="handleSubmit" class="user-form">
      <div class="form-group">
        <label for="username">Nome de Usuário:</label>
        <input type="text" id="username" v-model="user.username" required :disabled="isEditMode">
      </div>
      <div class="form-group">
        <label for="email">Email:</label>
        <input type="email" id="email" v-model="user.email" required>
      </div>
      
      <div class="form-group" v-if="!isEditMode">
        <label for="password">Senha:</label>
        <input type="password" id="password" v-model="user.password" required>
      </div>

      <div class="form-group" v-if="!isEditMode">
        <label for="confirm_password">Confirmar Senha:</label>
        <input type="password" id="confirm_password" v-model="confirmPassword" required />
      </div>

      <div class="form-group" v-if="isSuperuser || (!isSuperuser && !isEditMode) || isEditMode">
        <label for="estabelecimento">Estabelecimento:</label>
        <select 
          id="estabelecimento" 
          v-model="user.perfil.estabelecimento" 
          :required="!isSuperuser" 
          :disabled="!isSuperuser && !isEditMode"
        >
          <option :value="null">Selecione um estabelecimento</option>
          <option v-for="est in establishments" :key="est.id" :value="est.id">
            {{ est.nome }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="papel">Papel:</label>
        <select 
          id="papel" 
          v-model="user.perfil.papel" 
          required 
        >
          <option value="">Selecione um papel</option>
          <option value="gestor">Gestor</option>
          <option value="garcom">Garçom</option>
          <option value="cozinheiro">Cozinheiro</option>
          <option value="caixa">Caixa</option>
        </select>
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="successMessage" class="success-message">{{ successMessage }}</p> <div class="form-actions">
        <button type="submit" :disabled="loading" class="btn btn-primary">
          {{ loading ? 'Salvando...' : (isEditMode ? 'Salvar Alterações' : 'Adicionar Usuário') }}
        </button>
        <button type="button" @click="goBack" class="btn btn-secondary" :disabled="loading">Cancelar</button>
      </div>
    </form>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'UserForm',
  props: {
    userId: { // Virá da rota se estiver em modo de edição
      type: String, // IDs são UUIDs, então String é o tipo correto
      default: null
    }
  },
  data() {
    return {
      user: {
        username: '',
        email: '',
        password: '', // Apenas para adição, não deve ser exposto na edição
        perfil: {
          estabelecimento: null, // Inicializado como null, pois pode ser um UUID
          papel: '',
        },
      },
      confirmPassword: '', // Para confirmação de senha na criação
      establishments: [],
      loading: false,
      error: null,
      successMessage: null,
      isEditMode: false,
      isSuperuser: false,
      loggedInUserEstablishmentId: null, // Para gestores, para preencher o campo automaticamente
    };
  },
  async created() {
    // 1. Definir modo de edição se userId for fornecido via props
    if (this.userId) {
      this.isEditMode = true;
      await this.fetchUser(this.userId); // Buscar dados do usuário para edição
    }

    // 2. Sempre buscar o contexto do usuário logado (superusuário ou gestor)
    await this.fetchLoggedInUserContext();

    // 3. Buscar a lista completa de estabelecimentos:
    //    - Se for superusuário
    //    - OU se estiver em modo de edição (mesmo gestor, para ver o estabelecimento do editado)
    //    - OU se for um gestor adicionando um usuário (precisa da lista para o select)
    if (this.isSuperuser || this.isEditMode || (!this.isSuperuser && !this.isEditMode)) {
      await this.fetchEstablishments();
    }
    
    // 4. Preencher o estabelecimento para gestores em modo de adição
    //    Isso garante que o `v-model` do select receba o valor correto assim que os dados estiverem disponíveis.
    if (!this.isSuperuser && !this.isEditMode && this.loggedInUserEstablishmentId) {
      this.user.perfil.estabelecimento = this.loggedInUserEstablishmentId;
    }
  },
  methods: {
    async fetchEstablishments() {
      try {
        const response = await api.get('usuarios/estabelecimentos/');
        this.establishments = response.data.results;
      } catch (error) {
        console.error('Erro ao carregar estabelecimentos:', error);
        this.error = 'Não foi possível carregar os estabelecimentos.';
      }
    },
    async fetchLoggedInUserContext() {
      try {
        const username = localStorage.getItem('username');
        if (!username) {
          console.warn("Nome de usuário não encontrado no localStorage. Redirecionando para login.");
          this.$router.push('/login'); // Redireciona se não houver username
          return;
        }
        const response = await api.get(`usuarios/users/?username=${username}`);
        
        const currentUser = response.data.results && response.data.results.length > 0 ? response.data.results[0] : null;
        
        if (currentUser) {
          this.isSuperuser = currentUser.is_superuser;
          
          // Verifica se o perfil e o estabelecimento existem na resposta
          if (currentUser.perfil && currentUser.perfil.estabelecimento) {
            // O ID do estabelecimento vem como string (UUID)
            this.loggedInUserEstablishmentId = currentUser.perfil.estabelecimento; 
            
            // Se NÃO for superusuário E NÃO estiver no modo de edição (ou seja, gestor adicionando)
            // Pré-seleciona o estabelecimento do gestor no formulário.
            if (!this.isSuperuser && !this.isEditMode) {
              this.user.perfil.estabelecimento = this.loggedInUserEstablishmentId;
            }
          } else {
            console.warn("Perfil ou estabelecimento do usuário logado não encontrado.");
            // Se for gestor e não tiver estabelecimento no perfil, é um erro IMPEDITIVO para adicionar.
            if (!this.isSuperuser && !this.isEditMode) {
              this.error = "Seu perfil de gestor não tem um estabelecimento associado. Não é possível adicionar usuários.";
            }
          }
        } else {
          console.warn("Usuário logado não encontrado na resposta da API.");
          this.error = "Não foi possível carregar as informações do usuário logado. Faça login novamente.";
        }
      } catch (error) {
        console.error('Erro ao carregar contexto do usuário logado:', error);
        this.error = 'Erro ao carregar contexto do usuário logado. Tente novamente.';
      }
    },
    async fetchUser(userId) {
      this.loading = true;
      this.error = null;
      try {
        const response = await api.get(`usuarios/users/${userId}/`);
        this.user.username = response.data.username;
        this.user.email = response.data.email;
        // Não preencher senha em modo de edição por segurança
        
        if (response.data.perfil) {
          this.user.perfil.estabelecimento = response.data.perfil.estabelecimento; 
          this.user.perfil.papel = response.data.perfil.papel;
        }
      } catch (error) {
        console.error('Erro ao buscar usuário para edição:', error);
        this.error = 'Não foi possível carregar os dados do usuário para edição.';
      } finally {
        this.loading = false;
      }
    },
    async handleSubmit() {
      this.loading = true;
      this.error = null;
      this.successMessage = null;

      try {
        // Validação de senhas para criação de novo usuário
        if (!this.isEditMode && this.user.password !== this.confirmPassword) {
          this.error = "As senhas não coincidem.";
          this.loading = false;
          return;
        }

        let response;
        let userDataToSend = {
          username: this.user.username,
          email: this.user.email,
        };

        if (!this.isEditMode) {
          userDataToSend.password = this.user.password;
        }

        userDataToSend.perfil = {}; 

        if (!this.isSuperuser && !this.isEditMode) {
          if (this.loggedInUserEstablishmentId) {
            userDataToSend.perfil.estabelecimento = this.loggedInUserEstablishmentId; 
            console.log("DEBUG: (Força bruta) Estabelecimento para novo usuário (gestor):", userDataToSend.perfil.estabelecimento);
          } else {
            this.error = "Não foi possível determinar o estabelecimento do gestor logado.";
            this.loading = false;
            return;
          }
        } else {
          userDataToSend.perfil.estabelecimento = this.user.perfil.estabelecimento;
          console.log("DEBUG: (v-model) Estabelecimento:", userDataToSend.perfil.estabelecimento);
        }

        userDataToSend.perfil.papel = this.user.perfil.papel;

        if (!this.isEditMode && !this.isSuperuser && !userDataToSend.perfil.estabelecimento) { 
          this.error = "Não foi possível determinar o estabelecimento para o novo usuário. Verifique o perfil do gestor logado.";
          this.loading = false;
          return;
        }

        console.log('Dados a serem enviados para a API (FINAL):', userDataToSend); 

        if (this.isEditMode) {
          response = await api.put(`usuarios/users/${this.userId}/`, userDataToSend);
          this.successMessage = 'Usuário atualizado com sucesso!';
        } else {
          response = await api.post('usuarios/users/', userDataToSend);
          this.successMessage = 'Usuário adicionado com sucesso!';
          
          this.user = {
            username: '',
            email: '',
            password: '',
            perfil: { estabelecimento: null, papel: '' },
          };
          this.confirmPassword = ''; 
        }
        
      } catch (error) {
        console.error('Erro ao salvar usuário:', error.response ? error.response.data : error.message);
        this.error = 'Erro ao salvar usuário: ' + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message);
      } finally {
        this.loading = false;
      }
    },
    goBack() {
      this.$router.push('/users');
    }
  }
};
</script>

<style scoped>
/* Estilos gerais do formulário */
.user-form-container {
  padding: 20px;
  max-width: 700px;
  margin: 30px auto;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 25px;
  font-size: 2em;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.user-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 0; /* Ajustado para melhor controle com gap */
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
}

input[type="text"],
input[type="email"],
input[type="password"],
select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box; /* Garante que padding e border sejam incluídos na largura */
  font-size: 1em;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

input[type="text"]:focus,
input[type="email"]:focus,
input[type="password"]:focus,
select:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  outline: none;
}

input:disabled, select:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
  opacity: 0.8;
}

.form-actions {
  grid-column: 1 / -1; /* Ocupa todas as colunas */
  display: flex;
  justify-content: flex-end;
  gap: 15px; /* Espaço entre os botões */
  margin-top: 20px;
}

.btn {
  padding: 12px 25px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1em;
  font-weight: bold;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.btn-primary {
  background-color: #28a745; /* Verde */
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #218838;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: #6c757d; /* Cinza */
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #5a6268;
  transform: translateY(-2px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Mensagens de feedback */
.error-message, .success-message {
  grid-column: 1 / -1; /* Ocupa todas as colunas */
  margin-top: 15px;
  padding: 12px;
  border-radius: 6px;
  font-weight: bold;
  text-align: center;
  border: 1px solid transparent; /* Para consistência */
}

.error-message {
  background-color: #f8d7da; /* Vermelho claro */
  color: #721c24;
  border-color: #f5c6cb;
}

.success-message {
  background-color: #d4edda; /* Verde claro */
  color: #155724;
  border-color: #c3e6cb;
}

.loading {
  grid-column: 1 / -1;
  text-align: center;
  color: #007bff;
  font-weight: bold;
  margin-top: 15px;
}

/* Responsividade básica */
@media (max-width: 768px) {
  .user-form {
    grid-template-columns: 1fr; /* Uma coluna em telas menores */
  }
}
</style>