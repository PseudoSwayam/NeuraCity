import { useState, useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';
import axios from 'axios';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { AlertTriangle, TrendingUp, Activity } from 'lucide-react';

interface EventsPerDay {
  date: string;
  count: number;
}

interface EventsByModule {
  module: string;
  count: number;
}

interface Anomaly {
  timestamp_hour: string;
  event_count: number;
  details: string;
}

interface AnalyticsChartsProps {
  type: 'events-per-day' | 'events-by-module' | 'anomalies';
}

const COLORS = ['hsl(180 100% 50%)', 'hsl(195 100% 60%)', 'hsl(210 100% 70%)', 'hsl(225 100% 80%)'];

const AnalyticsCharts = ({ type }: AnalyticsChartsProps) => {
  const [eventsPerDay, setEventsPerDay] = useState<EventsPerDay[]>([]);
  const [eventsByModule, setEventsByModule] = useState<EventsByModule[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { getAuthHeaders } = useAuthStore();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const headers = getAuthHeaders();

        if (type === 'events-per-day') {
          const response = await axios.get('http://localhost:8002/stats/events_per_day', { 
            headers, 
            timeout: 10000 
          });
          
          const eventsPerDayArray = Object.entries(response.data).map(([date, count]) => ({
            date,
            count: count as number
          }));
          setEventsPerDay(eventsPerDayArray);
        } else if (type === 'events-by-module') {
          const response = await axios.get('http://localhost:8002/stats/events_by_module', { 
            headers, 
            timeout: 10000 
          });
          
          const eventsByModuleArray = Object.entries(response.data).map(([module, count]) => ({
            module,
            count: count as number
          }));
          setEventsByModule(eventsByModuleArray);
        } else if (type === 'anomalies') {
          const response = await axios.get('http://localhost:8002/stats/anomalies', { 
            headers, 
            timeout: 10000 
          });
          // Sort anomalies by timestamp (latest first)
          const sortedAnomalies = response.data.sort((a: Anomaly, b: Anomaly) => 
            new Date(b.timestamp_hour).getTime() - new Date(a.timestamp_hour).getTime()
          );
          setAnomalies(sortedAnomalies);
        }

      } catch (error) {
        console.error('Error fetching analytics:', error);
        setError('Failed to load data');
        
        // Fallback demo data
        if (type === 'events-per-day') {
          setEventsPerDay([
            { date: '2024-01-01', count: 45 },
            { date: '2024-01-02', count: 67 },
            { date: '2024-01-03', count: 23 },
            { date: '2024-01-04', count: 89 },
            { date: '2024-01-05', count: 56 },
          ]);
        } else if (type === 'events-by-module') {
          setEventsByModule([
            { module: 'CV Security', count: 156 },
            { module: 'Traffic Monitor', count: 89 },
            { module: 'Air Quality', count: 67 },
            { module: 'Noise Detection', count: 43 },
          ]);
        } else if (type === 'anomalies') {
          setAnomalies([
            { timestamp_hour: '2024-01-07T14:00:00Z', event_count: 95, details: 'Unusually high events detected' },
            { timestamp_hour: '2024-01-07T12:00:00Z', event_count: 87, details: 'Traffic pattern anomaly' },
            { timestamp_hour: '2024-01-07T09:00:00Z', event_count: 76, details: 'Air quality readings above normal' },
          ]);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [type]);

  const getAnomalyColor = (eventCount: number) => {
    if (eventCount >= 90) return 'text-destructive bg-destructive/10 border-destructive/30';
    if (eventCount >= 70) return 'text-warning bg-warning/10 border-warning/30';
    return 'text-primary bg-primary/10 border-primary/30';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3 border border-destructive/30 rounded-lg bg-destructive/10 text-destructive text-sm">
        <AlertTriangle className="h-4 w-4 inline mr-2" />
        {error} - Showing demo data
      </div>
    );
  }

  if (type === 'events-per-day') {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <TrendingUp className="h-4 w-4" />
          <span>Last 7 days</span>
        </div>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={eventsPerDay}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis 
              dataKey="date" 
              stroke="hsl(var(--muted-foreground))"
              fontSize={11}
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                color: 'hsl(var(--foreground))',
                fontSize: '12px'
              }}
            />
            <Bar dataKey="count" fill="hsl(180 100% 50%)" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (type === 'events-by-module') {
    return (
      <div className="space-y-4">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={eventsByModule}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={80}
              paddingAngle={5}
              dataKey="count"
            >
              {eventsByModule.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                color: 'hsl(var(--foreground))',
                fontSize: '12px'
              }}
              formatter={(value, name, props) => [
                `${value} events`,
                props.payload?.module || 'Source'
              ]}
            />
          </PieChart>
        </ResponsiveContainer>
        
        <div className="grid grid-cols-1 gap-1 text-xs">
          {eventsByModule.map((entry, index) => (
            <div key={entry.module} className="flex items-center gap-2">
              <div 
                className="w-2 h-2 rounded-full" 
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="text-muted-foreground truncate">{entry.module}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (type === 'anomalies') {
    return (
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {anomalies.length === 0 ? (
          <div className="text-center text-muted-foreground py-4">
            <Activity className="h-6 w-6 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No anomalies detected</p>
          </div>
        ) : (
          anomalies.map((anomaly, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border text-xs ${getAnomalyColor(anomaly.event_count)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="font-medium mb-1">
                    {anomaly.details}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {new Date(anomaly.timestamp_hour).toLocaleString()}
                  </div>
                </div>
                <span className="text-xs font-mono px-2 py-1 rounded bg-primary/20 text-primary ml-2">
                  {anomaly.event_count}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    );
  }

  return null;
};

export default AnalyticsCharts;