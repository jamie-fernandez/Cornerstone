import { createRouter, createWebHistory } from 'vue-router'
import PCharacter from '@/pages/PCharacter.vue'
import PMain from '@/pages/PMain.vue'
import PTemplates from '@/pages/PTemplates.vue'

const routes = [
    {
        path: '/',
        component: PMain,
        meta: { breadcrumb: 'Home' },
    },
    {
        path: '/templates',
        component: PTemplates,
        meta: { breadcrumb: 'Templates' },
    },
    {
        path: '/characters/:id',
        component: PCharacter,
        props: true,
        meta: {
            breadcrumb: 'Character Details',
            parent: '/templates',
        },
    },
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
})

export default router
