import { create } from 'zustand';

export interface Alert {
  id: string;
  timestamp: number;
  human_readable_message: string;
  raw_event_data: {
    event_type: string;
    payload: {
      location: string;
      camera_id?: string;
    };
  };
  coordinates?: [number, number];
}

interface AlertState {
  alerts: Alert[];
  isConnected: boolean;
  lastAlert: Alert | null;
  showToast: boolean;
  addAlert: (alert: Alert) => void;
  setConnectionStatus: (connected: boolean) => void;
  clearAlerts: () => void;
  setLastAlert: (alert: Alert | null) => void;
  setShowToast: (show: boolean) => void;
}

// Hardcoded locations for camera mapping
const CAMERA_LOCATIONS: Record<string, [number, number]> = {
  'LobbyCam-01': [40.7135, -74.0066],
  'Lab-01': [40.7150, -74.0070],
  'ParkingCam-A1': [40.7128, -74.0060],
  'ExitGate-02': [40.7140, -74.0075],
  'MainHall-Cam': [40.7145, -74.0065],
};

export const useAlertStore = create<AlertState>((set, get) => ({
  alerts: [],
  isConnected: false,
  lastAlert: null,
  showToast: false,

  addAlert: (alert) => {
    // Check if alert with same ID already exists to prevent duplicates
    const state = get();
    if (state.alerts.some(existingAlert => existingAlert.id === alert.id)) {
      return;
    }

    // Extract camera ID from location and get coordinates
    const cameraId = alert.raw_event_data.payload.camera_id || 
                    alert.raw_event_data.payload.location.split(' ')[0];
    
    const coordinates = CAMERA_LOCATIONS[cameraId];
    
    const alertWithCoords: Alert = {
      ...alert,
      coordinates,
    };

    set((state) => ({
      alerts: [alertWithCoords, ...state.alerts.slice(0, 19)], // Keep last 20 alerts
    }));
  },

  setConnectionStatus: (connected) => {
    set({ isConnected: connected });
  },

  clearAlerts: () => {
    set({ alerts: [] });
  },

  setLastAlert: (alert) => {
    set({ lastAlert: alert });
  },

  setShowToast: (show) => {
    set({ showToast: show });
  },
}));