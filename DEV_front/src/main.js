import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import Toaster from '@meforma/vue-toaster';
import axios from 'axios'
import VueAxios from 'vue-axios'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(Toaster)
app.use(VueAxios, axios)
app.mount('#app')


