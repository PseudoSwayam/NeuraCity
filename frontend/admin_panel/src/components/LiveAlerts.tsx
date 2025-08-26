import { useEffect, useRef, useState } from 'react';
import { useAlertStore, Alert } from '@/stores/alertStore';
import { useAuthStore } from '@/stores/authStore';
import { Wifi, WifiOff, AlertTriangle, Clock } from 'lucide-react';

const LiveAlerts = () => {
  const ws = useRef<WebSocket | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [lastAlert, setLastAlert] = useState<Alert | null>(null);
  const [showToast, setShowToast] = useState(false);

  const { token } = useAuthStore();
  const { addAlert, setConnectionStatus, isConnected, alerts } = useAlertStore();

  const connectWebSocket = () => {
    if (!token) {
      console.log('No token available for WebSocket connection');
      return;
    }

    try {
      const wsUrl = `ws://localhost:8003/ws/alerts?token=${token}`;
      console.log('Connecting to WebSocket:', wsUrl);
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus(true);
        setReconnectAttempts(0);
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          const alert: Alert = {
            id: `${Date.now()}-${Math.random()}`,
            timestamp: Date.now(),
            human_readable_message: data.human_readable_message,
            raw_event_data: data.raw_event_data,
          };

          addAlert(alert);
          setLastAlert(alert);
          
          // Show toast notification
          setShowToast(true);
          setTimeout(() => setShowToast(false), 7000);
          
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus(false);
        
        // Attempt to reconnect with exponential backoff
        if (reconnectAttempts < 5) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
          setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connectWebSocket();
          }, delay);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus(false);
      };

    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionStatus(false);
    }
  };

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [token]);

  return (
    <div className="h-full flex flex-col">
      {/* Connection Status */}
      <div className="glass-panel p-3 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isConnected ? (
              <>
                <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
                <span className="text-xs text-success font-mono">LIVE</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-destructive rounded-full" />
                <span className="text-xs text-destructive font-mono">
                  {reconnectAttempts > 0 ? `RECONNECTING` : 'DISCONNECTED'}
                </span>
              </>
            )}
          </div>
          <div className="text-xs text-muted-foreground font-mono">
            {alerts.length} alerts
          </div>
        </div>
      </div>

      {/* Recent Alerts List */}
      <div className="flex-1 overflow-y-auto space-y-3">
        {alerts.length === 0 ? (
          <div className="text-center text-muted-foreground py-8">
            <AlertTriangle className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No alerts received</p>
          </div>
        ) : (
          alerts.slice(0, 20).map((alert) => {
            const getTimeAgo = (timestamp: number) => {
              const now = Date.now();
              const diff = now - timestamp;
              const minutes = Math.floor(diff / (1000 * 60));
              
              if (minutes < 1) return 'Just now';
              if (minutes === 1) return '1 min ago';
              if (minutes < 60) return `${minutes} mins ago`;
              
              const hours = Math.floor(minutes / 60);
              if (hours === 1) return '1 hour ago';
              if (hours < 24) return `${hours} hours ago`;
              
              const days = Math.floor(hours / 24);
              return `${days} day${days > 1 ? 's' : ''} ago`;
            };

            const getSeverityColor = (eventType: string) => {
              if (eventType.includes('security') || eventType.includes('intrusion')) {
                return 'border-destructive/50 bg-destructive/10';
              }
              if (eventType.includes('traffic') || eventType.includes('violation')) {
                return 'border-warning/50 bg-warning/10';
              }
              return 'border-primary/50 bg-primary/10';
            };

            return (
              <div
                key={alert.id}
                className={`alert-item border-l-4 ${getSeverityColor(alert.raw_event_data.event_type)}`}
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between">
                    <h4 className="font-medium text-sm leading-tight">
                      {alert.human_readable_message}
                    </h4>
                    <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">
                      {getTimeAgo(alert.timestamp)}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>{new Date(alert.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Toast Notification */}
      {showToast && lastAlert && (
        <div className="fixed bottom-6 right-6 z-50 neura-toast max-w-md">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-warning mt-0.5 flex-shrink-0" />
            <div>
              <div className="font-medium text-foreground">
                {lastAlert.raw_event_data.event_type.replace(/_/g, ' ')}
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                {lastAlert.human_readable_message}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveAlerts;