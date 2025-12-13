<script setup>
    import { faker } from '@faker-js/faker'
    import { onMounted, ref } from 'vue'
    import { useRoute } from 'vue-router'
    import BreadcrumbNavigation from '../components/BreadcrumbNavigation.vue'
    import createRandomCharacter from '../composables/classes/character'

    const route = useRoute()
    const characterId = route.params.id

    const character = ref(null)
    const newTag = ref('')
    const fileInputRef = ref(null)

    const images = ref([
        {
            id: '1',
            name: 'Character Portrait 1.png',
            url: faker.image.avatar(),
            tags: ['portrait', 'full body'],
            characterTags: ['adventurous', 'brave'],
        },
        {
            id: '2',
            name: 'Character Portrait 2.png',
            url: faker.image.avatar(),
            tags: ['close-up', 'smiling'],
            characterTags: ['friendly', 'kind'],
        },
        {
            id: '3',
            name: 'Character Action 1.png',
            url: faker.image.avatar(),
            tags: ['action', 'fighting'],
            characterTags: ['strong', 'determined'],
        },
        {
            id: '4',
            name: 'Character Action 2.png',
            url: faker.image.avatar(),
            tags: ['running', 'fast'],
            characterTags: ['agile', 'quick'],
        },
    ])

    const selectedImages = ref([])
    const isImageInfoVisible = ref(false)
    const currentImage = ref(null)
    const isIndividualTaggingVisible = ref(false)
    const currentTaggingImage = ref(null)
    const newImageTag = ref('')
    const newImageTagInput = ref(null)

    onMounted(() => {
        const randomCharacters = createRandomCharacter(1)
        const randomCharacter = randomCharacters[0]
        randomCharacter.id = characterId
        if (!randomCharacter.tags) {
            randomCharacter.tags = []
        }
        character.value = randomCharacter

        for (let i = 5; i <= 10; i++) {
            images.value.push({
                id: i.toString(),
                name: `Character Image ${i}.png`,
                url: faker.image.avatar(),
                tags: [faker.word.adjective(), faker.word.noun()],
                characterTags: character.value.tags,
            })
        }
    })

    function formatDate(date) {
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        }
        return new Intl.DateTimeFormat('en-US', options).format(date)
    }

    // Image gallery functions
    function showImageInfo(image) {
        currentImage.value = image
        isImageInfoVisible.value = true
    }

    function selectImage(imageId) {
        const index = selectedImages.value.indexOf(imageId)
        if (index > -1) {
            selectedImages.value.splice(index, 1)
        } else {
            selectedImages.value.push(imageId)
        }
    }

    function selectAllImages() {
        if (selectedImages.value.length === images.value.length) {
            selectedImages.value = []
        } else {
            selectedImages.value = images.value.map((img) => img.id)
        }
    }

    function bulkEdit() {
        alert(`Editing ${selectedImages.value.length} images`)
    }

    function bulkTag() {
        alert(`Tagging ${selectedImages.value.length} images`)
    }

    function bulkDelete() {
        images.value = images.value.filter(
            (img) => !selectedImages.value.includes(img.id),
        )
        selectedImages.value = []
        alert(`Deleted ${selectedImages.value.length} images`)
    }

    function bulkArchive() {
        alert(`Archived ${selectedImages.value.length} images`)
    }

    function archiveImage(imageId) {
        if (confirm('Are you sure you want to archive this image?')) {
            const imageIndex = images.value.findIndex(
                (img) => img.id === imageId,
            )
            if (imageIndex !== -1) {
                images.value[imageIndex].archived = true
                const index = selectedImages.value.indexOf(imageId)
                if (index > -1) selectedImages.value.splice(index, 1)
            }
        }
    }

    function deleteImage(imageId) {
        if (confirm('Are you sure you want to delete this image?')) {
            images.value = images.value.filter((img) => img.id !== imageId)
            const index = selectedImages.value.indexOf(imageId)
            if (index > -1) selectedImages.value.splice(index, 1)
        }
    }

    function downloadImage(image) {
        if (image.originalFile) {
            const url = URL.createObjectURL(image.originalFile)
            const a = document.createElement('a')
            a.href = url
            a.download = image.name
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            URL.revokeObjectURL(url)
        } else {
            const a = document.createElement('a')
            a.href = image.url
            a.download = image.name
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
        }
    }

    function bulkDownload() {
        const selectedImageObjects = images.value.filter((img) =>
            selectedImages.value.includes(img.id),
        )
        selectedImageObjects.forEach(downloadImage)
    }

    function uploadImages(event) {
        const files = event.target.files
        if (!files || files.length === 0) return

        Array.from(files).forEach(processAndOptimizeImage)

        if (images.value.length > 0) {
            const lastImage = images.value[images.value.length - 1]
            showTaggingDialog(lastImage)
        }
    }

    function processAndOptimizeImage(file) {
        const reader = new FileReader()
        reader.onload = (e) => {
            images.value.push({
                id: faker.string.uuid(),
                name: file.name,
                url: e.target?.result || '',
                originalFile: file,
                tags: [],
                characterTags: character.value?.tags || [],
            })
        }
        reader.readAsDataURL(file)
    }

    // Tag editing
    function addImageTag() {
        if (newImageTag.value.trim() && currentTaggingImage.value) {
            const tag = newImageTag.value.trim()
            if (!currentTaggingImage.value.tags.includes(tag)) {
                currentTaggingImage.value.tags.push(tag)
                newImageTag.value = ''
                setTimeout(() => {
                    if (newImageTagInput.value) newImageTagInput.value.focus()
                }, 50)
            }
        }
    }

    function removeImageTag(tag) {
        if (currentTaggingImage.value) {
            currentTaggingImage.value.tags =
                currentTaggingImage.value.tags.filter((t) => t !== tag)
        }
    }

    function showTaggingDialog(image) {
        currentTaggingImage.value = image
        isIndividualTaggingVisible.value = true
        setTimeout(() => {
            if (newImageTagInput.value) newImageTagInput.value.focus()
        }, 300)
    }

    function closeTaggingDialog() {
        isIndividualTaggingVisible.value = false
        currentTaggingImage.value = null
        newImageTag.value = ''
    }

    // Character tags
    function addTag() {
        if (newTag.value.trim() && character.value) {
            const tag = newTag.value.trim()
            if (!character.value.tags.includes(tag)) {
                character.value.tags.push(tag)
                newTag.value = ''
            }
        }
    }

    function removeTag(tag) {
        if (character.value) {
            character.value.tags = character.value.tags.filter((t) => t !== tag)
        }
    }
</script>

<template>
    <v-container fluid>
        <BreadcrumbNavigation />
        <!-- Character Header -->
        <v-row class="mb-6" align="center">
            <v-col cols="12" md="2">
                <v-avatar :image="character?.avatar" :size="120" class="mb-4" />
            </v-col>
            <v-col cols="12" md="10">
                <h1 class="text-h4 mb-2">
                    {{ character?.name }}
                </h1>
                <div class="d-flex flex-wrap gap-2 mb-2">
                    <v-chip v-for="tag in character?.tags" :key="tag" color="primary" size="small">
                        {{ tag }}
                    </v-chip>
                </div>
                <v-row>
                    <v-col cols="12" sm="6">
                        <v-card variant="outlined" class="pa-4">
                            <h3 class="text-h6 mb-2">
                                Character Attributes
                            </h3>
                            <p>
                                <strong>Sex:</strong>
                                {{ character?.sex || "N/A" }}
                            </p>
                            <p>
                                <strong>Created:</strong>
                                {{
                                    character?.createdAt
                                        ? formatDate(character.createdAt)
                                        : "N/A"
                                }}
                            </p>
                            <p>
                                <strong>Updated:</strong>
                                {{
                                    character?.updatedAt
                                        ? formatDate(character.updatedAt)
                                        : "N/A"
                                }}
                            </p>
                        </v-card>
                    </v-col>
                    <v-col cols="12" sm="6">
                        <v-card variant="outlined" class="pa-4">
                            <h3 class="text-h6 mb-2 d-flex align-center">
                                Character Tags
                                <v-spacer />
                                <v-text-field v-model="newTag" label="Add new tag" density="compact" variant="outlined"
                                    hide-details style="max-width: 200px;" @keyup.enter="addTag" />
                                <v-btn icon="$plus" size="small" color="primary" class="ms-2" @click="addTag" />
                            </h3>
                            <div class="d-flex flex-wrap gap-2 mt-4">
                                <v-chip v-for="tag in character?.tags" :key="tag" color="primary" size="small" closable
                                    @click:close="removeTag(tag)">
                                    {{ tag }}
                                </v-chip>
                            </div>
                        </v-card>
                    </v-col>
                </v-row>
            </v-col>
        </v-row>

        <!-- Image Gallery Actions -->
        <v-row class="mb-4">
            <v-col cols="12">
                <v-toolbar density="compact" class="mb-4">
                    <v-btn class="me-2" prepend-icon="$upload" variant="outlined" @click="() => fileInputRef?.click()">
                        Upload
                    </v-btn>

                    <v-spacer />

                    <v-btn :disabled="selectedImages.length === 0" class="me-2" prepend-icon="$pencil"
                        variant="outlined" @click="bulkEdit">
                        Edit
                    </v-btn>

                    <v-btn :disabled="selectedImages.length === 0" class="me-2" prepend-icon="$tag" variant="outlined"
                        @click="bulkTag">
                        Tag
                    </v-btn>

                    <v-btn :disabled="selectedImages.length === 0" class="me-2" prepend-icon="$delete"
                        variant="outlined" @click="bulkDelete">
                        Delete
                    </v-btn>

                    <v-btn :disabled="selectedImages.length === 0" class="me-2" prepend-icon="$archive"
                        variant="outlined" @click="bulkArchive">
                        Archive
                    </v-btn>

                    <v-btn :disabled="selectedImages.length === 0" class="me-2" prepend-icon="$download"
                        variant="outlined" @click="bulkDownload">
                        Download
                    </v-btn>

                    <v-btn variant="text" @click="selectAllImages">
                        {{
                            selectedImages.length === images.length
                                ? "Deselect All"
                                : "Select All"
                        }}
                    </v-btn>
                </v-toolbar>

                <input ref="fileInputRef" type="file" accept="image/*,video/*" multiple style="display: none"
                    @change="uploadImages">
            </v-col>
        </v-row>

        <!-- Image Gallery -->
        <v-row>
            <v-col v-for="image in images" :key="image.id" cols="6" sm="4" md="3" lg="2">
                <v-card :class="{ selected: selectedImages.includes(image.id), archived: image.archived }"
                    class="image-card" @click="selectImage(image.id)">
                    <v-img :src="image.url" height="150" cover @click.stop="showImageInfo(image)" />
                    <v-card-title class="text-truncate pa-2">
                        {{ image.name }}
                    </v-card-title>
                    <v-card-actions class="pa-2">
                        <v-btn icon="$tag" size="x-small" variant="text" @click.stop="showTaggingDialog(image)" />
                        <v-btn icon="$download" size="x-small" variant="text" @click.stop="downloadImage(image)" />
                        <v-btn icon="$archive" size="x-small" variant="text" @click.stop="archiveImage(image.id)" />
                        <v-btn icon="$delete" size="x-small" variant="text" color="error"
                            @click.stop="deleteImage(image.id)" />
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-row>
    </v-container>

    <!-- Image Info Dialog -->
    <v-dialog v-model="isImageInfoVisible" max-width="600">
        <v-card v-if="currentImage">
            <v-img :src="currentImage.url" height="400" cover />
            <v-card-title>{{ currentImage.name }}</v-card-title>
            <v-card-text>
                <h3 class="text-h6">
                    Image Tags
                </h3>
                <div class="d-flex flex-wrap gap-2 mb-4">
                    <v-chip v-for="tag in currentImage.tags" :key="tag" color="secondary" size="small">
                        {{ tag }}
                    </v-chip>
                </div>

                <h3 class="text-h6">
                    Character Tags
                </h3>
                <div class="d-flex flex-wrap gap-2">
                    <v-chip v-for="charTag in currentImage.characterTags" :key="charTag" color="primary" size="small">
                        {{ charTag }}
                    </v-chip>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-btn prepend-icon="$download" color="secondary" @click="downloadImage(currentImage)">
                    Download
                </v-btn>
                <v-btn prepend-icon="$archive" @click="archiveImage(currentImage?.id)">
                    Archive
                </v-btn>
                <v-btn prepend-icon="$delete" color="error" @click="deleteImage(currentImage?.id)">
                    Delete
                </v-btn>
                <v-spacer />
                <v-btn text="Close" @click="isImageInfoVisible = false" />
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- Individual Image Tagging Dialog -->
    <v-dialog v-model="isIndividualTaggingVisible" max-width="600">
        <v-card v-if="currentTaggingImage">
            <v-img :src="currentTaggingImage.url" height="300" cover />
            <v-card-title>{{ currentTaggingImage.name }}</v-card-title>
            <v-card-text>
                <h3 class="text-h6 mb-2">
                    Image Tags
                </h3>
                <div class="d-flex flex-wrap gap-2 mb-4">
                    <v-chip v-for="tag in currentTaggingImage.tags" :key="tag" color="secondary" size="small" closable
                        @click:close="removeImageTag(tag)">
                        {{ tag }}
                    </v-chip>
                </div>
                <div class="d-flex align-center">
                    <v-text-field ref="newImageTagInput" v-model="newImageTag" label="Add new tag" density="compact"
                        variant="outlined" hide-details @keyup.enter="addImageTag" />
                    <v-btn icon="$plus" size="small" color="primary" class="ms-2" @click="addImageTag" />
                </div>
            </v-card-text>
            <v-card-actions>
                <v-spacer />
                <v-btn text="Close" @click="closeTaggingDialog" />
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<style scoped>
    .image-card {
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }

    .image-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .image-card.selected {
        border: 2px solid #1976d2;
        box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.5);
    }

    .image-card.archived {
        opacity: 0.5;
        filter: grayscale(100%);
    }

    .gap-2 {
        gap: 0.5rem;
    }
</style>
