import { createRouter, createWebHistory } from 'vue-router'
import PMain from '@/pages/PMain.vue'

const routes = [
    {
        path: '/',
        component: PMain,
        meta: { breadcrumb: 'Home' },
    },
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
})

export default router
