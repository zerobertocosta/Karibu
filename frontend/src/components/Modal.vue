<!-- frontend/src/components/Modal.vue -->
<template>
  <div v-if="isVisible" class="modal-overlay">
    <div class="modal-content">
      <h3 class="modal-title">{{ title }}</h3>
      <p class="modal-message">{{ message }}</p>
      <div class="modal-actions">
        <button v-if="type === 'confirm'" @click="handleCancel" class="btn-modal cancel">Cancelar</button>
        <button @click="handleConfirm" :class="['btn-modal', type === 'alert' ? 'ok' : 'confirm']">
          {{ type === 'alert' ? 'OK' : 'Confirmar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppModal', // Renomeado para evitar conflito com 'Modal' de terceiros
  props: {
    title: {
      type: String,
      default: 'Mensagem',
    },
    message: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      default: 'alert', // 'alert' ou 'confirm'
      validator: (value) => ['alert', 'confirm'].includes(value),
    },
  },
  data() {
    return {
      isVisible: false,
      resolvePromise: null,
      rejectPromise: null,
    };
  },
  methods: {
    show() {
      this.isVisible = true;
      return new Promise((resolve, reject) => {
        this.resolvePromise = resolve;
        this.rejectPromise = reject;
      });
    },
    handleConfirm() {
      this.isVisible = false;
      if (this.resolvePromise) {
        this.resolvePromise(true);
      }
    },
    handleCancel() {
      this.isVisible = false;
      if (this.resolvePromise) {
        this.resolvePromise(false);
      }
    },
    // Método para fechar o modal externamente (útil para casos de carregamento, etc.)
    hide() {
      this.isVisible = false;
      if (this.rejectPromise) { // Se ainda houver uma promise pendente, rejeita
        this.rejectPromise(new Error('Modal fechado externamente.'));
      }
    }
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000; /* Garante que o modal fique por cima de tudo */
}

.modal-content {
  background-color: #fff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  text-align: center;
  max-width: 400px;
  width: 90%; /* Responsivo */
  font-family: 'Arial', sans-serif;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-title {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.5em;
  font-weight: bold;
}

.modal-message {
  color: #555;
  margin-bottom: 25px;
  line-height: 1.6;
  font-size: 1em;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn-modal {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 1em;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.1s ease;
  min-width: 100px;
}

.btn-modal.ok, .btn-modal.confirm {
  background-color: #007bff;
  color: white;
}

.btn-modal.ok:hover, .btn-modal.confirm:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
}

.btn-modal.cancel {
  background-color: #6c757d;
  color: white;
}

.btn-modal.cancel:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
}
</style>
