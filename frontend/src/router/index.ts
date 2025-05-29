// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import StartPage from '@/pages/StartPage.vue'
import SearchPage from '@/pages/SearchPage.vue'

const routes = [
  { path: '/',      name: 'Home',   component: StartPage },
  { path: '/search', name: 'Search', component: SearchPage },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
