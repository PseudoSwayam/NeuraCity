import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useAlertStore, Alert } from '@/stores/alertStore';

// Mapbox access token - user needs to provide their own
// mapboxgl.accessToken = 'your-mapbox-token-here';

const NeuroMap = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);
  const [needsToken, setNeedsToken] = useState(false);
  const [userToken, setUserToken] = useState('');

  const { alerts } = useAlertStore();

  useEffect(() => {
    if (!mapContainer.current) return;

    // Check if Mapbox token is set
    if (!mapboxgl.accessToken || mapboxgl.accessToken.includes('DEMO') || mapboxgl.accessToken === 'your-mapbox-token-here') {
      setNeedsToken(true);
      return;
    }

    try {
      // Initialize map with dark theme
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/dark-v11',
        center: [-74.0066, 40.7135], // NYC coordinates
        zoom: 15,
        pitch: 45,
        bearing: 0,
        projection: 'globe' as any,
      });

      // Add navigation controls
      map.current.addControl(
        new mapboxgl.NavigationControl({
          visualizePitch: true,
        }),
        'top-right'
      );

      // Add atmosphere effect
      map.current.on('style.load', () => {
        if (map.current) {
          map.current.setFog({
            color: 'hsl(220 27% 8%)',
            'high-color': 'hsl(180 100% 50%)',
            'horizon-blend': 0.1,
          });
        }
      });

      // Clear the token requirement if map loads successfully
      map.current.on('load', () => {
        setNeedsToken(false);
      });

    } catch (error) {
      console.error('Mapbox initialization failed:', error);
      setNeedsToken(true);
    }

    return () => {
      if (map.current) {
        map.current.remove();
      }
    };
  }, [userToken]);

  // Update markers when alerts change
  useEffect(() => {
    if (!map.current) return;

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Add new markers for alerts with coordinates
    alerts.forEach((alert, index) => {
      if (alert.coordinates) {
        const markerElement = createMarkerElement(alert);
        
        const marker = new mapboxgl.Marker({
          element: markerElement,
          anchor: 'center'
        })
          .setLngLat([alert.coordinates[1], alert.coordinates[0]])
          .addTo(map.current!);

        // Add popup
        const popup = new mapboxgl.Popup({
          offset: 25,
          className: 'neura-popup'
        }).setHTML(`
          <div class="neura-panel p-4 text-sm max-w-xs">
            <div class="font-medium text-primary mb-2">${alert.raw_event_data.event_type}</div>
            <div class="text-foreground mb-2">${alert.human_readable_message}</div>
            <div class="text-xs text-muted-foreground">
              ${new Date(alert.timestamp).toLocaleTimeString()}
            </div>
          </div>
        `);

        marker.setPopup(popup);
        markersRef.current.push(marker);

        // Fly to newest alert
        if (index === 0 && map.current) {
          map.current.flyTo({
            center: [alert.coordinates[1], alert.coordinates[0]],
            zoom: 17,
            pitch: 60,
            duration: 2000,
          });
        }
      }
    });
  }, [alerts]);

  const createMarkerElement = (alert: Alert) => {
    const el = document.createElement('div');
    el.className = 'neura-marker';
    
    const severity = getSeverity(alert.raw_event_data.event_type);
    const color = getSeverityColor(severity);
    
    el.innerHTML = `
      <div class="relative w-8 h-8 flex items-center justify-center">
        <div class="absolute inset-0 rounded-full ${color} neura-pulse opacity-60"></div>
        <div class="absolute inset-1 rounded-full ${color} shadow-neura-glow"></div>
        <div class="relative z-10 w-3 h-3 rounded-full bg-white"></div>
      </div>
    `;
    
    return el;
  };

  const getSeverity = (eventType: string): 'high' | 'medium' | 'low' => {
    if (eventType.includes('CRITICAL') || eventType.includes('SECURITY')) return 'high';
    if (eventType.includes('WARNING') || eventType.includes('ALERT')) return 'medium';
    return 'low';
  };

  const getSeverityColor = (severity: 'high' | 'medium' | 'low'): string => {
    switch (severity) {
      case 'high': return 'bg-destructive';
      case 'medium': return 'bg-warning';
      case 'low': return 'bg-primary';
    }
  };

  const handleTokenSubmit = () => {
    if (userToken.trim()) {
      mapboxgl.accessToken = userToken;
      setNeedsToken(false);
      // Force re-render
      window.location.reload();
    }
  };

  // Always show the iframe instead of token input
  return (
    <div className="relative w-full h-full">
      <iframe 
        src="http://localhost:8004/"
        className="absolute inset-0 w-full h-full border-0 rounded-lg overflow-hidden z-0"
        title="NeuraCity Map"
        allow="geolocation"
      />
    </div>
  );

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="absolute inset-0 rounded-lg overflow-hidden z-0" />
      
      {/* Map Overlay UI */}
      <div className="absolute top-4 left-4 neura-panel p-4 backdrop-blur-sm">
        <h2 className="text-lg font-semibold text-primary mb-2">NeuroMap</h2>
        <div className="text-sm text-muted-foreground">
          <div>Active Alerts: <span className="text-foreground font-mono">{alerts.length}</span></div>
          <div>Coverage: <span className="text-success">98.7%</span></div>
        </div>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 neura-panel p-3 backdrop-blur-sm">
        <div className="text-xs text-muted-foreground mb-2">Alert Severity</div>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-destructive"></div>
            <span>Critical</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-warning"></div>
            <span>Warning</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-primary"></div>
            <span>Info</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NeuroMap;