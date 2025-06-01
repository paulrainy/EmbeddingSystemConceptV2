<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from '@/api';

type Status = 'loading' | 'up' | 'down';
const status = ref<Status>('loading');

onMounted(async () => {
  try {
    const { data } = await api.get('/healthz');      // эндпоинт уже есть в бэке :contentReference[oaicite:0]{index=0}
    status.value = data.status === 'ok' ? 'up' : 'down';
  } catch {
    status.value = 'down';
  }
});
</script>

<template>
  <section class="flex flex-col items-center gap-6 py-10">
    <h1 class="text-4xl font-bold">Embedding System UI</h1>

    <p v-if="status === 'loading'">⏳ Проверяем API…</p>
    <p v-else-if="status === 'up'"  class="text-green-600">✅ API доступен</p>
    <p v-else                       class="text-red-600">❌ API недоступен</p>

    <RouterLink
      to="/search"
      class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg shadow">
      Перейти к поиску
    </RouterLink>
  </section>
</template>
