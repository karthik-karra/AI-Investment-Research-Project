// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import PrimeVue from 'primevue/config';

// Import PrimeVue v3 CSS
import 'primevue/resources/themes/aura-light-noir/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';

// Import components
import Button from 'primevue/button';

import store from './store'
import router from './router'

const app = createApp(App).use(router).use(store);

app.use(PrimeVue);

// Register components globally
app.component('PButton', Button);

app.mount('#app');