import { createRouter, createWebHashHistory } from 'vue-router'
import PMain from '@/pages/PMain.vue'

const routes = [
    {
        path: '/',
        component: PMain,
        meta: { breadcrumb: 'Home' },
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

export default router
    