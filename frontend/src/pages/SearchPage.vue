<!-- src/pages/SearchPage.vue -->
<template>
  <div class="max-w-2xl mx-auto py-10">
    <h1 class="text-2xl font-bold mb-6">Поиск тест-кейсов</h1>

    <!-- Используем ваш компонент ввода (он сам эмитит событие) -->
    <SearchInput @search="onSearch" />

    <!-- Плейсхолдер под результаты -->
    <div class="mt-6 p-4 bg-gray-50 rounded-lg border border-dashed border-gray-300 text-gray-500 text-center">
      Результаты поиска появятся здесь, когда API будет готов
    </div>
  </div>
</template>

<script lang="ts" setup>

//import SearchInput from '@/components/SearchInput.vue'

// Обработчик пока только логит запрос
function onSearch(queryText: string) {
  console.log('Запрос на поиск (заглушка):', queryText)
  // TODO: здесь позже будет axios.post() к бекенду
}
</script>

<style scoped>
/* По желанию можно добавить свою стилизацию */
</style>
