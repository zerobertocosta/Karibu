<template>
  <div v-if="message" :class="['toast-message', messageTypeClass]">
    <p>{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'ToastMessage',
  props: {
    message: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'info', // info, success, error
      validator: (value) => ['info', 'success', 'error'].includes(value)
    }
  },
  computed: {
    messageTypeClass() {
      switch (this.type) {
        case 'success':
          return 'bg-green-500 text-white';
        case 'error':
          return 'bg-red-500 text-white';
        case 'info':
        default:
          return 'bg-blue-500 text-white';
      }
    }
  }
};
</script>

<style scoped>
.toast-message {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 15px 30px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  z-index: 1000; /* Garante que fique acima de outros elementos */
  animation: fadeinout 4s forwards; /* Animação de fade */
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-width: 250px;
}

@keyframes fadeinout {
  0% { opacity: 0; transform: translateX(-50%) translateY(20px); }
  10% { opacity: 1; transform: translateX(-50%) translateY(0); }
  90% { opacity: 1; transform: translateX(-50%) translateY(0); }
  100% { opacity: 0; transform: translateX(-50%) translateY(20px); }
}
</style>