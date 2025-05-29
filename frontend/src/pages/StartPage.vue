<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-6">
    <!-- Заголовок -->
    <h1 class="text-3xl font-bold mb-8">Панель управления</h1>

    <!-- Кнопка пересчёта эмбеддингов -->
    <button
      @click="triggerReindex"
      :disabled="isLoading"
      class="flex items-center px-6 py-3 mb-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition disabled:opacity-50"
    >
      <!-- Состояние: Loading › Spinner -->
      <svg
        v-if="isLoading"
        class="animate-spin h-5 w-5 mr-2 text-white"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8v8H4z"
        />
      </svg>

      <!-- Состояние: Success › Checkmark -->
      <svg
        v-else-if="isSuccess"
        class="h-5 w-5 mr-2 text-green-300"
        xmlns="http://www.w3.org/2000/svg"
        fill="none" viewBox="0 0 24 24"
        stroke="currentColor" stroke-width="3"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
      </svg>

      <!-- Текст кнопки -->
      <span v-if="isLoading">Пересчёт…</span>
      <span v-else-if="isSuccess">Готово!</span>
      <span v-else>Пересчитать эмбеддинги</span>
    </button>

    <!-- Кнопка навигации на страницу поиска -->
    <button
      @click="goToSearch"
      class="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg transition"
    >
      Перейти к поиску
    </button>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const isLoading = ref(false)
const isSuccess = ref(false)
const router = useRouter()

async function triggerReindex() {
  isLoading.value = true
  isSuccess.value = false
//   try {
//     // Вызываем API FastAPI
//     await axios.post(
//       `${import.meta.env.VITE_API_URL}/api/v1/admin/reindex`,
//       { filter: {} }
//     )
//     // Успешно
//     isSuccess.value = true
//   } catch (err) {
//     console.error('Reindex error', err)
//     alert('Ошибка при пересчёте эмбеддингов')
//   } finally {
//     isLoading.value = false
//     // Сброс состояния success через 2 секунды
//     if (isSuccess.value) {
//       setTimeout(() => {
//         isSuccess.value = false
//       }, 2000)
//     }
//   }
}

function goToSearch() {
  router.push({ name: 'Search' })
}
</script>
