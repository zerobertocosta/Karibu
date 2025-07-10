<template>
  <div class="about">
    <h1>Sobre o Karibu</h1>
    <p>O Karibu é uma aplicação de gestão completa para restaurantes, desenvolvida para simplificar suas operações.</p>
    <p>Nossa missão é ajudar seu negócio a prosperar através de ferramentas intuitivas e eficientes.</p>
  </div>
</template>

<script>
export default {
  name: 'AboutView'
}
</script>

<style scoped>
.about {
  padding: 40px;
  text-align: center;
  background-color: #fffaf0;
  border-radius: 8px;
  margin: 30px auto;
  max-width: 800px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
h1 {
  color: #333;
  margin-bottom: 20px;
}
p {
  color: #555;
  font-size: 1.1em;
  margin-bottom: 10px;
}
</style>