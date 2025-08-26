import { useState, useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';
import axios from 'axios';
import { Activity, AlertCircle, CheckCircle2, HelpCircle, RefreshCw } from 'lucide-react';

interface ModuleHealth {
  module: string;
  status: 'Healthy' | 'Unhealthy' | 'Unreachable' | 'Unknown';
}

const ModuleHealthStatus = () => {
  const [modules, setModules] = useState<ModuleHealth[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { getAuthHeaders } = useAuthStore();

  const fetchModuleHealth = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const headers = getAuthHeaders();
      console.log('Fetching module health with headers:', headers);

      const response = await axios.get(
        'http://localhost:8002/stats/module_health',
        { 
          headers,
          timeout: 10000
        }
      );

      console.log('Module health response:', response.data);
      setModules(response.data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching module health:', error);
      
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNREFUSED') {
          setError('Cannot connect to InsightCloud API (localhost:8002)');
        } else if (error.response?.status === 401) {
          setError('Authentication failed - please login again');
        } else {
          setError(`API Error: ${error.response?.status || error.message}`);
        }
      } else {
        setError('Failed to fetch module status');
      }
      
      // Fallback demo data
      setModules([
        { module: 'neuranlp_agent', status: 'Healthy' },
        { module: 'cv_watchtower', status: 'Unhealthy' },
        { module: 'traffic_monitor', status: 'Healthy' },
        { module: 'air_quality_sensor', status: 'Unknown' },
        { module: 'noise_detector', status: 'Healthy' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModuleHealth();
    
    // Poll every 30 seconds
    const interval = setInterval(fetchModuleHealth, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: ModuleHealth['status']) => {
    switch (status) {
      case 'Healthy':
        return <CheckCircle2 className="h-4 w-4 text-success" />;
      case 'Unhealthy':
      case 'Unreachable':
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      case 'Unknown':
        return <HelpCircle className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: ModuleHealth['status']) => {
    switch (status) {
      case 'Healthy':
        return 'text-success';
      case 'Unhealthy':
      case 'Unreachable':
        return 'text-destructive';
      case 'Unknown':
        return 'text-muted-foreground';
    }
  };

  const healthyCount = modules.filter(m => m.status === 'Healthy').length;
  const totalCount = modules.length;

  return (
    <div className="space-y-3">
      {error && (
        <div className="p-2 border border-destructive/30 rounded bg-destructive/10 text-destructive text-xs">
          <AlertCircle className="h-3 w-3 inline mr-1" />
          {error} - Showing demo data
        </div>
      )}

      {/* Overall Status */}
      <div className="glass-panel p-3">
        <div className="text-xs text-muted-foreground">System Status</div>
        <div className="flex items-center justify-between mt-1">
          <span className="text-lg font-mono">
            <span className="text-success">{healthyCount}</span>
            <span className="text-muted-foreground">/{totalCount}</span>
          </span>
          <span className="text-xs text-muted-foreground">
            {totalCount > 0 ? Math.round((healthyCount / totalCount) * 100) : 0}% Up
          </span>
        </div>
      </div>

      {/* Module List */}
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {modules.map((module, index) => (
          <div
            key={module.module}
            className="glass-panel p-3 transition-all duration-300 hover:border-primary/40 hover:shadow-lg"
            style={{ 
              animation: `fadeInUp 0.3s ease-out ${index * 0.1}s both` 
            }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getStatusIcon(module.status)}
                <span className="text-xs font-medium text-foreground">
                  {module.module === 'iot_pulsenet' 
                    ? 'IOT_pulsenet' 
                    : module.module.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                  }
                </span>
              </div>
              
              <span className={`text-xs font-mono ${getStatusColor(module.status)}`}>
                {module.status.toUpperCase()}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Last Update */}
      {lastUpdate && (
        <div className="text-xs text-muted-foreground text-center">
          Updated: {lastUpdate.toLocaleTimeString()}
        </div>
      )}
    </div>
  );
};

export default ModuleHealthStatus;