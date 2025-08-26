import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useAlertStore, Alert } from '@/stores/alertStore';
import { useAuthStore } from '@/stores/authStore';

// Hardcoded locations for campus mapping
const locations: Record<string, [number, number]> = {
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

// Event styles configuration
const eventStyles: Record<string, { color: string; icon: string }> = {
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

// Filtered event types that should appear on the map
const mapEventTypes = [
  'CV_SECURITY_ALERT', 
  'NLP_SECURITY_ALERT', 
  'IOT_SECURITY_ALERT', 
  'FALL_DETECTED', 
  'VIOLENCE_DETECTED', 
  'FIRE_SMOKE_DETECTED', 
  'INTRUSION_DETECTED', 
  'ABANDONED_OBJECT'
];

interface MapAlert extends Alert {
  style: { color: string; icon: string };
}

// Custom hook to control map flyTo animation
const FlyToAlert = ({ alert }: { alert: MapAlert | null }) => {
  const map = useMap();
  
  useEffect(() => {
    if (alert && alert.coordinates) {
      map.flyTo([alert.coordinates[0], alert.coordinates[1]], 17, {
        duration: 2,
        easeLinearity: 0.5
      });
    }
  }, [alert, map]);
  
  return null;
};

// Create custom Leaflet icon
const createCustomIcon = (style: { color: string; icon: string }) => {
  return L.divIcon({
    html: `
      <div class="relative w-8 h-8 flex items-center justify-center">
        <div class="absolute inset-0 rounded-full neura-pulse opacity-60" style="background-color: ${style.color}"></div>
        <div class="absolute inset-1 rounded-full shadow-neura-glow" style="background-color: ${style.color}"></div>
        <div class="relative z-10 flex items-center justify-center w-6 h-6 rounded-full bg-background text-xs">
          ${style.icon}
        </div>
      </div>
    `,
    className: 'neura-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
  });
};

const NeuroMap = () => {
  const [mapAlerts, setMapAlerts] = useState<MapAlert[]>([]);
  const [latestAlert, setLatestAlert] = useState<MapAlert | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const { alerts, addAlert, setConnectionStatus } = useAlertStore();
  const { token } = useAuthStore();

  // WebSocket connection for live alerts
  useEffect(() => {
    if (!token) return;

    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(`ws://localhost:8003/ws/alerts?token=${token}`);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
          setConnectionStatus(true);
        };

        ws.onmessage = (event) => {
          try {
            const alertData = JSON.parse(event.data);
            
            // Check if this event type should be displayed on the map
            const eventType = alertData.raw_event_data?.event_type;
            if (mapEventTypes.includes(eventType)) {
              // Find coordinates for this alert
              const locationKey = alertData.raw_event_data?.payload?.location || 
                                alertData.raw_event_data?.payload?.camera_id;
              
              if (locationKey) {
                // Find matching location (case-insensitive)
                const coordinates = Object.entries(locations).find(([key]) => 
                  key.toLowerCase().includes(locationKey.toLowerCase()) ||
                  locationKey.toLowerCase().includes(key.toLowerCase())
                )?.[1];

                if (coordinates) {
                  const style = eventStyles[eventType] || eventStyles.DEFAULT;
                  const newAlert: MapAlert = {
                    ...alertData,
                    coordinates,
                    style
                  };

                  // Add to store
                  addAlert(newAlert);
                  
                  // Update map-specific state
                  setMapAlerts(prev => [newAlert, ...prev.slice(0, 19)]);
                  setLatestAlert(newAlert);
                }
              }
            } else {
              // Still add to general alerts even if not shown on map
              addAlert(alertData);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
          setConnectionStatus(false);
          
          // Attempt to reconnect after 3 seconds
          setTimeout(() => {
            if (token) connectWebSocket();
          }, 3000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
          setConnectionStatus(false);
        };

      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        setIsConnected(false);
        setConnectionStatus(false);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [token, addAlert, setConnectionStatus]);

  return (
    <div className="relative w-full h-full">
      {/* Leaflet Map Container */}
      <MapContainer
        center={[40.7135, -74.0066]}
        zoom={15}
        className="absolute inset-0 w-full h-full z-0"
        zoomControl={false}
        attributionControl={false}
      >
        {/* CartoDB Dark Matter Tiles */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
          subdomains={['a', 'b', 'c', 'd']}
        />
        
        {/* Map Alert Markers */}
        {mapAlerts.map((alert, index) => (
          <Marker
            key={`${alert.id}-${index}`}
            position={[alert.coordinates![0], alert.coordinates![1]]}
            icon={createCustomIcon(alert.style)}
          >
            <Popup className="neura-popup">
              <div className="neura-panel p-3 text-sm max-w-xs bg-background border border-border rounded-lg">
                <div className="font-medium text-primary mb-2 flex items-center gap-2">
                  <span>{alert.style.icon}</span>
                  {alert.raw_event_data.event_type}
                </div>
                <div className="text-foreground mb-2">{alert.human_readable_message}</div>
                <div className="text-xs text-muted-foreground">
                  {new Date(alert.timestamp).toLocaleString()}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
        
        {/* Auto-fly to latest alert */}
        <FlyToAlert alert={latestAlert} />
      </MapContainer>

      {/* Map Overlay UI */}
      <div className="absolute top-4 left-4 neura-panel p-4 backdrop-blur-sm z-10">
        <h2 className="text-lg font-semibold text-primary mb-2">NeuroMap</h2>
        <div className="text-sm text-muted-foreground space-y-1">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success neura-pulse' : 'bg-destructive'}`}></div>
            <span>{isConnected ? 'LIVE' : 'DISCONNECTED'}</span>
          </div>
          <div>Active Alerts: <span className="text-foreground font-mono">{mapAlerts.length}</span></div>
          <div>Coverage: <span className="text-success">98.7%</span></div>
        </div>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 neura-panel p-3 backdrop-blur-sm z-10">
        <div className="text-xs text-muted-foreground mb-2">Alert Types</div>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#e74c3c' }}></div>
            <span>Critical</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#f39c12' }}></div>
            <span>Warning</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#9b59b6' }}></div>
            <span>IoT</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#3498db' }}></div>
            <span>Info</span>
          </div>
        </div>
      </div>

      {/* Zoom Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-1 z-10">
        <button className="neura-panel p-2 hover:bg-muted transition-colors">
          <span className="text-lg">+</span>
        </button>
        <button className="neura-panel p-2 hover:bg-muted transition-colors">
          <span className="text-lg">−</span>
        </button>
      </div>
    </div>
  );
};

export default NeuroMap;