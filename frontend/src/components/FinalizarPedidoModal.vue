<!-- frontend/src/components/FinalizarPedidoModal.vue -->
<template>
  <div v-if="isVisible" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Finalizar Pedido {{ pedidoId }}</h3>
        <button @click="cancel" class="close-button">&times;</button>
      </div>
      <div class="modal-body">
        <p class="total-display">Total do Pedido: <strong>R$ {{ formatCurrency(pedidoTotal) }}</strong></p>
        
        <div class="form-group">
          <label for="gorjeta">Gorjeta (R$):</label>
          <input 
            type="number" 
            id="gorjeta" 
            v-model.number="gorjetaInput" 
            min="0" 
            step="0.01" 
            placeholder="Ex: 5.00"
            class="modal-input"
          />
        </div>
        
        <div class="form-group">
          <label for="observacoes">Observações / Elogios:</label>
          <textarea 
            id="observacoes" 
            v-model="observacoesInput" 
            rows="3" 
            placeholder="Ex: 'Ótimo atendimento do garçom João!'"
            class="modal-textarea"
          ></textarea>
        </div>
        
        <p v-if="gorjetaInput !== null && gorjetaInput >= 0" class="final-total">
          Total com Gorjeta: <strong>R$ {{ formatCurrency(parseFloat(pedidoTotal) + parseFloat(gorjetaInput)) }}</strong>
        </p>

        <p v-if="errorMessage" class="error-message-modal">{{ errorMessage }}</p>

      </div>
      <div class="modal-footer">
        <button @click="confirm" class="btn-action confirm-button">Confirmar Finalização</button>
        <button @click="cancel" class="btn-action cancel-button">Cancelar</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FinalizarPedidoModal',
  props: {
    pedidoId: {
      type: Number,
      required: true
    },
    pedidoTotal: {
      type: [Number, String], // Pode ser número ou string vindo do backend
      required: true
    }
  },
  data() {
    return {
      isVisible: false,
      gorjetaInput: null, // Inicializa como null para indicar que não foi preenchido
      observacoesInput: '',
      resolve: null, // Para guardar a função de resolve da Promise
      errorMessage: '',
    };
  },
  methods: {
    // Método para exibir o modal. Retorna uma Promise que resolve com os dados ou false
    show() {
      this.isVisible = true;
      this.gorjetaInput = null; // Reseta ao abrir
      this.observacoesInput = ''; // Reseta ao abrir
      this.errorMessage = '';
      return new Promise(resolver => {
        this.resolve = resolver;
      });
    },
    // Confirma a finalização
    confirm() {
      if (this.gorjetaInput !== null && (isNaN(this.gorjetaInput) || this.gorjetaInput < 0)) {
        this.errorMessage = 'Por favor, insira um valor de gorjeta válido (número positivo).';
        return;
      }

      this.isVisible = false;
      this.resolve({
        confirmed: true,
        gorjeta: this.gorjetaInput,
        observacoes: this.observacoesInput
      });
    },
    // Cancela a finalização
    cancel() {
      this.isVisible = false;
      this.resolve({ confirmed: false });
    },
    // Formata valores monetários para exibição
    formatCurrency(value) {
      const num = typeof value === 'string' ? parseFloat(value) : value;
      if (isNaN(num) || num === null || num === undefined) {
        return '0,00';
      }
      return parseFloat(num).toFixed(2).replace('.', ',');
    }
  }
};
</script>

<style scoped>
/* Estilos para o overlay do modal (fundo escuro) */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6); /* Fundo semi-transparente */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000; /* Garante que o modal fique acima de tudo */
  backdrop-filter: blur(3px); /* Efeito de desfoque no fundo */
}

/* Estilos para o conteúdo do modal */
.modal-content {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  width: 90%; /* Largura padrão, ajusta para mobile */
  max-width: 500px; /* Largura máxima para desktop */
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.3s ease-out; /* Animação de entrada */
}

/* Animação de entrada */
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}

/* Cabeçalho do modal */
.modal-header {
  background-color: #007bff;
  color: white;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3em;
}

.close-button {
  background: none;
  border: none;
  color: white;
  font-size: 1.8em;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.2s ease;
}

.close-button:hover {
  color: #f0f0f0;
}

/* Corpo do modal */
.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px; /* Espaçamento entre os elementos do formulário */
}

.total-display {
  text-align: center;
  font-size: 1.2em;
  color: #333;
  margin-bottom: 10px;
}

.total-display strong {
  color: #28a745; /* Verde para o total */
  font-size: 1.1em;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: bold;
  margin-bottom: 5px;
  color: #555;
  font-size: 0.95em;
}

.modal-input, .modal-textarea {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1em;
  width: 100%;
  box-sizing: border-box; /* Garante que padding não aumente a largura */
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.modal-input:focus, .modal-textarea:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
  outline: none;
}

.modal-textarea {
  resize: vertical; /* Permite redimensionar verticalmente */
  min-height: 80px;
}

.final-total {
  text-align: center;
  font-size: 1.3em;
  font-weight: bold;
  color: #007bff;
  margin-top: 10px;
}

.final-total strong {
  color: #28a745; /* Verde para o total final */
  font-size: 1.1em;
}

.error-message-modal {
  color: #dc3545;
  font-size: 0.85em;
  text-align: center;
  margin-top: -10px; /* Ajusta a margem para ficar mais perto do input */
}

/* Rodapé do modal */
.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end; /* Alinha botões à direita */
  gap: 10px; /* Espaçamento entre os botões */
  background-color: #f8f9fa;
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
}

/* Estilos dos botões no modal (reutilizando btn-action) */
.btn-action {
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 0.95em;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.confirm-button {
  background-color: #28a745; /* Verde para confirmar */
  color: white;
}

.confirm-button:hover {
  background-color: #218838;
}

.cancel-button {
  background-color: #dc3545; /* Vermelho para cancelar */
  color: white;
}

.cancel-button:hover {
  background-color: #c82333;
}

/* Responsividade */
@media (max-width: 480px) {
  .modal-content {
    width: 95%; /* Um pouco mais largo em telas muito pequenas */
  }

  .modal-header h3 {
    font-size: 1.1em;
  }

  .close-button {
    font-size: 1.5em;
  }

  .modal-body {
    padding: 15px;
  }

  .btn-action {
    padding: 8px 15px;
    font-size: 0.9em;
  }

  .modal-footer {
    flex-direction: column-reverse; /* Inverte a ordem dos botões no mobile */
    gap: 8px;
  }
}
</style>
