<script setup>
    import { faker } from '@faker-js/faker'
    import { ref } from 'vue'
    import { useRouter } from 'vue-router'
    import BreadcrumbNavigation from '@/components/BreadcrumbNavigation.vue'
    import createRandomCharacter from '@/composables/classes/character'

    const router = useRouter()
    const search = ref('')
    const headers = [
        { title: 'Name', key: 'name' },
        { title: 'Sex', key: 'sex' },
        {
            title: 'Tags',
            key: 'tags',
            value: (item) => item.tags?.join(', ') || '',
        },
        { title: 'Avatar', key: 'avatar', sortable: false },
        {
            title: 'Created At',
            key: 'createdAt',
            value: (item) => formatDate(item.createdAt),
        },
        {
            title: 'Updated At',
            key: 'updatedAt',
            value: (item) => formatDate(item.updatedAt),
        },
        { title: 'Actions', key: 'actions', sortable: false },
    ]

    const characters = ref(createRandomCharacter(15))

    function formatDate(date) {
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        }
        return new Intl.DateTimeFormat('en-US', options).format(date)
    }

    function add() {
        // creates a random template for testing
        const newCharacter = createRandomCharacter()[0]
        newCharacter.id = faker.string.uuid()
        characters.value.push(newCharacter)
        router.push(`/characters/${newCharacter.id}`)
    }

    function edit(id) {
        router.push(`/characters/${id}`)
    }

    function remove(id) {
        characters.value = characters.value.filter((item) => item.id !== id)
    }
</script>

<template>
    <v-container fluid>
        <BreadcrumbNavigation />
        <v-data-table v-model:search="search" :filter-keys="['name']" :headers="headers" :items="characters">
            <template #top>
                <v-toolbar class="pa-4 border-lg rounded-xl" flat>
                    <v-btn class="me-2" prepend-icon="$plus" rounded="lg" text="Create New Character Template" border
                        @click="add" />

                    <v-text-field v-model="search" density="compact" label="Search" prepend-inner-icon="$magnify"
                        variant="solo-filled" flat hide-details single-line />
                </v-toolbar>
            </template>

            <template #[`header.actions`]>
                <div class="text-end">
                    Actions
                </div>
            </template>

            <template #[`item.avatar`]="{ item }">
                <v-img :src="item.avatar" :width="50" :height="50" cover />
            </template>

            <template #[`item.actions`]="{ item }">
                <div class="d-flex ga-2 justify-end">
                    <v-icon color="medium-emphasis" icon="$pencil" size="small" @click="edit(item.id)" />

                    <v-icon color="medium-emphasis" icon="$delete" size="small" @click="remove(item.id)" />
                </div>
            </template>
        </v-data-table>
    </v-container>
</template>
