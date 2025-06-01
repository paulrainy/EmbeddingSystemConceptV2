<script setup lang="ts">
import { ref } from 'vue';
import { api } from '@/api';

const collection = ref('');
const query      = ref('');
const mode       = ref<'semantic' | 'idx' | 'inner_id'>('semantic');
const results    = ref<any[]>([]);
const isLoading  = ref(false);
const error      = ref<string|null>(null);

const search = async () => {
  error.value = null;
  isLoading.value = true;
  try {
    const { data } = await api.post('/milvus/search', {
      collection: collection.value,
      mode,
      ...(mode === 'semantic'
        ? { vector: query.value.split(',').map(Number) } // пример; подстрой под себя
        : mode === 'idx'
          ? { idx: query.value.split(',').map(Number) }
          : { inner_id: Number(query.value) }),
    });
    results.value = data.results;
  } catch (e: any) {
    error.value = e.message ?? 'Ошибка запроса';
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <section class="flex flex-col gap-6">
    <h2 class="text-2xl font-semibold">Поиск в Milvus</h2>

    <!-- форма -->
    <div class="flex flex-col gap-4 max-w-xl">
      <input v-model="collection" placeholder="Название коллекции" class="input" />
      <select v-model="mode" class="input">
        <option value="semantic">semantic (vector)</option>
        <option value="idx">idx</option>
        <option value="inner_id">inner_id</option>
      </select>
      <input v-model="query" placeholder="Запрос" class="input" />
      <button @click="search" class="btn" :disabled="isLoading">
        {{ isLoading ? 'Ищу…' : 'Найти' }}
      </button>
    </div>

    <!-- сообщения -->
    <p v-if="error" class="text-red-600">{{ error }}</p>

    <!-- результаты -->
    <pre v-if="results.length" class="bg-zinc-900/50 p-4 rounded-lg overflow-x-auto">
{{ JSON.stringify(results, null, 2) }}
    </pre>
  </section>
</template>

<style scoped>
.input {
  @apply border border-zinc-400 rounded-lg px-3 py-2;
}
.btn {
  @apply bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg;
}
</style>
