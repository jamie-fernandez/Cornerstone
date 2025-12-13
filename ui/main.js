import 'vuetify/styles'
import 'unfonts.css'

// https://vuetifyjs.com/en/features/icon-fonts/#creating-a-custom-icon-set
import {
    mdiArchive,
    mdiDelete,
    mdiDownload,
    mdiMagnify,
    mdiPencil,
    mdiPlus,
    mdiTag,
    mdiUpload,
    mdiVideoInputComponent,
} from '@mdi/js'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'
import App from '@/App.vue'
import router from '@/router'

const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'mdi',
        aliases: {
            ...aliases,
            delete: mdiDelete,
            pencil: mdiPencil,
            magnify: mdiMagnify,
            videoInputComponent: mdiVideoInputComponent,
            plus: mdiPlus,
            tag: mdiTag,
            archive: mdiArchive,
            download: mdiDownload,
            upload: mdiUpload,
        },
        sets: {
            mdi,
        },
    },
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')
