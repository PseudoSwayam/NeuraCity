// File: modules/neuromap/frontend/src/main.js

import { createApp } from 'vue'
import App from './App.vue'
import 'leaflet/dist/leaflet.css';
import { Icon } from 'leaflet';

// 1. Manually import the icon asset paths directly.
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

// 2. Re-construct Leaflet's default icon object, telling it to use the
Icon.Default.mergeOptions({
  iconRetinaUrl: iconRetinaUrl,
  iconUrl: iconUrl,
  shadowUrl: shadowUrl,
});

createApp(App).mount('#app')