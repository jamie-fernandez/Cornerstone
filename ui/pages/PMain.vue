<script setup>
    import { useRouter } from 'vue-router'

    const router = useRouter()

    const buttons = [
        { text: 'Templates', handler: () => router.push('/templates') },
        {
            text: 'Quit',
            handler: async () => await window.pywebview?.api?.quit(),
        },
    ]
</script>

<template>
    <v-main class="d-flex align-center justify-center h-100">
        <v-container class="d-flex flex-column align-center">
            <v-btn
                v-for="btn in buttons"
                :key="btn.text"
                class="mb-2"
                width="25%"
                @click="btn.handler"
            >
                {{ btn.text }}
            </v-btn>
        </v-container>
    </v-main>
</template>
