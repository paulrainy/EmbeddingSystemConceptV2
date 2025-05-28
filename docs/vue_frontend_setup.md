# Vue 3 + TypeScript + Tailwind CSS — интеграция фронта

## 0. Предпосылки  
* Бэкенд FastAPI запущен на `localhost:8000` (энд‑поинт `/search`).  
* Milvus + Redis подняты через Docker Compose.  
* Python‑окружение/Poetry уже настроены.

---

## 1. Инициализация проекта Vue 3 + TypeScript

```bash
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install
```

---

## 2. Установка Tailwind CSS

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

`tailwind.config.js`

```js
export default {
  content: ['./index.html','./src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: { extend: {} },
  plugins: [],
}
```

`src/assets/index.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

## 3. Типы API

`src/types/search.ts`

```ts
export interface SearchHit { id: number; score: number; snippet: string }
export interface SearchResponse { hits: SearchHit[] }
```

---

## 4. Компоненты

- `components/SearchInput.vue`
- `components/SearchResults.vue`
- `pages/SearchPage.vue`
- `src/main.ts`

*(см. детальный код выше)*

---

## 5. .env для фронта

```
VITE_API_URL=http://localhost:8000
```

---

## 6. CORS FastAPI

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods=['*'],
    allow_headers=['*'],
)
```

---

## 7. Запуск

```bash
# API
poetry run uvicorn app.main:app --reload
# Frontend
cd frontend && npm run dev
```

---

## 8. Docker‑Compose сервис (dev)

```yaml
frontend:
  image: node:20-alpine
  working_dir: /app
  volumes: [ "./frontend:/app" ]
  command: sh -c "npm install && npm run dev -- --host 0.0.0.0"
  ports: [ "5173:5173" ]
  environment:
    VITE_API_URL: http://localhost:8000
  networks: [ milvus-net ]
```

---

## 9. Продакшн‑сборка

```bash
cd frontend
npm run build   # dist/ с html+js+css
```

Раздавать через nginx или `StaticFiles` FastAPI.

---

## 10. Дальнейшие улучшения

| Функция | Библиотека |
|---------|------------|
| Routing | vue-router |
| State   | pinia |
| UI‑kit  | shadcn/ui или Headless UI |
| Tests   | vitest + @testing-library/vue |
