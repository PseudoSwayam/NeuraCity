<template>
  <!-- The main container for the entire map display -->
  <div id="map-container">
    <l-map ref="map" v-model:zoom="zoom" :center="center" :use-global-leaflet="false">
      <!-- This pulls the beautiful dark map tiles from CartoDB's free service -->
      <l-tile-layer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        layer-type="base"
        name="OpenStreetMap"
      ></l-tile-layer>

      <!-- This component dynamically loops through active alerts and displays a marker for each one -->
      <l-marker v-for="alert in activeAlerts" :key="alert.id" :lat-lng="alert.coords">
        <!-- This defines the custom HTML icon for our marker, including the pulsing animation -->
        <l-icon :icon-size="[40, 40]" class-name="custom-leaflet-icon">
          <div class="marker-container">
            <div class="marker-pulse" :style="{ backgroundColor: alert.style.color }"></div>
            <div class="marker-icon">{{ alert.style.icon }}</div>
          </div>
        </l-icon>
        <!-- This creates the popup that appears when you click a marker -->
        <l-popup>
          <div class="popup-content">
            <h3>{{ alert.eventType }}</h3>
            <p>{{ alert.message }}</p>
          </div>
        </l-popup>
      </l-marker>
    </l-map>
  </div>
  
  <!-- UI Overlays -->
  <div id="connection-status" :class="{ connected: isConnected, error: isError }">
    <div class="dot"></div>
    <div class="text">LIVE FEED: {{ connectionStatus }}</div>
  </div>
  
  <div id="latest-alert-banner" v-if="latestAlert" :class="{ visible: showLatestAlert }">
    <h2>LATEST ALERT &nbsp; <span class="event-icon" :style="{ backgroundColor: latestAlertStyle.color }">{{ latestAlertStyle.icon }}</span></h2>
    <p>{{ latestAlert }}</p>
  </div>
</template>

<script setup>
// Imports from Vue and Leaflet libraries
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LMarker, LIcon, LPopup } from "@vue-leaflet/vue-leaflet";

// --- CORE CONFIGURATION ---
const ALERTS_WEBSOCKET_URL = "ws://localhost:8003/ws/alerts";
const MAX_ALERTS_ON_MAP = 15; // Max markers to show to avoid clutter

// Creative Simulation: Define key lat/long coordinates for fictional campus locations
const locations = {
  "LobbyCam-01": [40.7135, -74.0066],
  "Fall Cam": [40.7135, -74.0066],
  "Courtyard-01": [40.7145, -74.0055],
  "Loitering Cam": [40.7145, -74.0055],
  "Plaza-01": [40.7125, -74.0045],
  "Abandoned Bag Cam": [40.7125, -74.0045],
  "Alley-01": [40.7130, -74.0080],
  "Fight Cam": [40.7130, -74.0080],
  "Lab-01": [40.7150, -74.0070],
  "Fire Cam": [40.7150, -74.0070],
  "Entrance-01": [40.7138, -74.0040],
  "Normal Activity Cam": [40.7138, -74.0040],
  "Main Gate": [40.7130, -74.0035],
  "Main Library": [40.7128, -74.0075],
  "Iot_pulsenet-01": [40.7140, -74.0060]
};

// Map event types to specific colors and icons for stunning visual cues
const eventStyles = {
  FALL_DETECTED: { color: '#e74c3c', icon: '🚨' },
  VIOLENCE_DETECTED: { color: '#e74c3c', icon: '💥' },
  FIRE_SMOKE_DETECTED: { color: '#f39c12', icon: '🔥' },
  INTRUSION_DETECTED: { color: '#f39c12', icon: '🚫' },
  ABANDONED_OBJECT: { color: '#f39c12', icon: '👜' },
  CV_SECURITY_ALERT: { color: '#e74c3c', icon: '🚨' },
  NLP_SECURITY_ALERT: { color: '#3498db', icon: '💬' },
  IOT_SECURITY_ALERT: { color: '#9b59b6', icon: '❤️‍🩹' },
  IOT_HEART_RATE_HIGH: { color: '#9b59b6', icon: '❤️‍🔥' },
  IOT_GAS_ALERT: { color: '#9b59b6', icon: '💨' },
  DEFAULT: { color: '#3498db', icon: 'ℹ️' },
};

// --- VUE REACTIVITY SETUP ---
const zoom = ref(17);
const center = ref([40.7140, -74.0060]);
const map = ref(null); // Reference to the map object for API calls like flyTo

// Connection Status
const connectionStatus = ref('Connecting...');
const isConnected = ref(false);
const isError = ref(false);

// Live Alert State
const latestAlert = ref('');
const latestAlertStyle = reactive({ color: '#3498db', icon: 'ℹ️' });
const showLatestAlert = ref(false);
const activeAlerts = ref([]);
let alertIdCounter = 0;
let socket = null;

// --- WEBSOCKET & MAP LOGIC ---
const handleIncomingAlert = (alertData) => {
  const message = alertData.human_readable_message;
  latestAlert.value = message;

  const rawEvent = alertData.raw_event_data || {};
  const payload = rawEvent.payload || {};
  const eventType = rawEvent.event_type || 'DEFAULT';

  // --- Map the event to a location on our fictional campus ---
  let primaryLocationString = (payload.camera_id || payload.location || "").toLowerCase();
  if (!primaryLocationString) {
    console.warn("Received event with no location info:", payload);
    return;
  }

  const locationKey = Object.keys(locations).find(key => primaryLocationString.includes(key.toLowerCase()));
  
  if (!locationKey) {
    console.warn(`Could not map location string "${primaryLocationString}" to a known coordinate.`);
    return;
  }
  
  const coords = locations[locationKey];
  
  // --- Create and add the new alert marker ---
  alertIdCounter++;
  const newAlert = {
    id: alertIdCounter,
    coords: coords,
    eventType: eventType,
    message: message,
    style: eventStyles[eventType] || eventStyles['DEFAULT']
  };
  
  activeAlerts.value.push(newAlert);
  if (activeAlerts.value.length > MAX_ALERTS_ON_MAP) {
    activeAlerts.value.shift();
  }

  // --- Trigger animations ---
  if (map.value && map.value.leafletObject) {
    map.value.leafletObject.flyTo(coords, 18, { duration: 2.5 });
  }

  latestAlertStyle.color = newAlert.style.color;
  latestAlertStyle.icon = newAlert.style.icon;
  showLatestAlert.value = true;
  setTimeout(() => { showLatestAlert.value = false }, 7000); // Hide banner after 7 seconds
};

const connectWebSocket = () => {
  socket = new WebSocket(ALERTS_WEBSOCKET_URL);

  socket.onopen = () => {
    isConnected.value = true;
    isError.value = false;
    connectionStatus.value = 'Live';
  };
  socket.onmessage = (event) => {
    handleIncomingAlert(JSON.parse(event.data));
  };
  socket.onclose = () => {
    isConnected.value = false;
    connectionStatus.value = 'Reconnecting...';
    setTimeout(connectWebSocket, 5000);
  };
  socket.onerror = () => {
    isConnected.value = false;
    isError.value = true;
    connectionStatus.value = 'Connection Failed';
    socket.close();
  };
};

// --- VUE LIFECYCLE HOOKS ---
onMounted(() => {
  connectWebSocket();
});
onUnmounted(() => {
  if (socket) socket.close();
});
</script>

<style>
/* Base Styles */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  overflow: hidden;
}

/* Map Container takes up the full screen */
#map-container {
  position: absolute; top: 0; bottom: 0;
  width: 100%;
  z-index: 0;
}

/* Base styles for UI overlays */
#connection-status, #latest-alert-banner {
  position: absolute;
  background: rgba(10, 10, 20, 0.85);
  color: #f0f0f0;
  padding: 10px 15px;
  border-radius: 8px;
  backdrop-filter: blur(5px);
  z-index: 1000;
  box-shadow: 0 4px 15px rgba(0,0,0,0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Connection Status Indicator */
#connection-status {
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
}
#connection-status .dot {
  width: 12px;
  height: 12px;
  background-color: #e74c3c; /* Red */
  border-radius: 50%;
  margin-right: 10px;
  transition: background-color 0.5s;
}
#connection-status.connected .dot {
  background-color: #2ecc71; /* Green */
  animation: pulse-green 2s infinite;
}

/* Live Alert Banner at the Bottom */
#latest-alert-banner {
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%) translateY(200%);
  width: 90%;
  max-width: 700px;
  transition: transform 0.5s ease-in-out;
}
#latest-alert-banner.visible {
  transform: translateX(-50%) translateY(0);
}
#latest-alert-banner h2 {
  margin: 0 0 5px 0;
  font-size: 1.1em;
  color: #fff;
  display: flex;
  align-items: center;
}
#latest-alert-banner .event-icon {
  display: inline-block;
  font-size: 1em;
  width: 28px;
  height: 28px;
  border-radius: 5px;
  text-align: center;
  line-height: 28px;
  margin-left: 10px;
}
#latest-alert-banner p {
  margin: 0;
  font-size: 1em;
  color: #ccc;
}


/* Custom Animated Map Marker */
.custom-leaflet-icon {
  border: none;
  background: none;
}
.marker-container {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.marker-icon {
  font-size: 24px;
  text-shadow: 0 0 5px black;
  position: relative;
  z-index: 2;
  animation: drop-in 0.5s ease-out;
}
.marker-pulse {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  position: absolute;
  z-index: 1;
  opacity: 0.8;
  transform-origin: center center;
  animation: pulse-animation 1.8s infinite cubic-bezier(0.2, 0.8, 0.7, 1);
}
.leaflet-popup-content-wrapper {
  background: rgba(25, 25, 35, 0.9);
  color: #f0f0f0;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.5);
}
.leaflet-popup-content-wrapper .leaflet-popup-content {
  padding: 10px 15px;
}
.leaflet-popup-content h3 { margin-top: 0; }
.leaflet-popup-tip-container .leaflet-popup-tip {
  background: rgba(25, 25, 35, 0.9);
}

@keyframes pulse-animation {
  0% { transform: scale(0.3); opacity: 0.8; }
  80% { transform: scale(2); opacity: 0; }
  100% { opacity: 0; }
}

@keyframes drop-in {
  0% { transform: translateY(-50px) scale(0.5); opacity: 0; }
  100% { transform: translateY(0) scale(1); opacity: 1; }
}
@keyframes pulse-green {
  0% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(46, 204, 113, 0); }
  100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
}

</style>