import { useState } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { useAlertStore } from '@/stores/alertStore';
import { Navigate } from 'react-router-dom';
import { ChevronDown, ChevronRight, LogOut, User, Activity, TrendingUp, AlertTriangle, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import NeuroMap from './NeuroMap';
import LiveAlerts from './LiveAlerts';
import ModuleHealthStatus from './ModuleHealthStatus';
import AnalyticsCharts from './AnalyticsCharts';
import Logo from './Logo';

const Dashboard = () => {
  const { isAuthenticated, logout, user } = useAuthStore();
  const { lastAlert, showToast } = useAlertStore();
  const [healthOpen, setHealthOpen] = useState(true);
  const [trendsOpen, setTrendsOpen] = useState(false);
  const [modulesOpen, setModulesOpen] = useState(false);
  const [anomaliesOpen, setAnomaliesOpen] = useState(false);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="h-screen bg-background relative overflow-hidden">
      {/* Background NeuroMap */}
      <div className="absolute inset-0">
        <NeuroMap />
      </div>

      {/* Floating Header */}
      <header className="absolute top-4 left-4 right-4 z-50 fade-in-up">
        <div className="glass-header px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Logo size="sm" showText={true} />
              <div className="flex items-center gap-2 text-sm text-primary">
                <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
                Live Feed: Connected
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <User className="h-4 w-4" />
                <span>Agent: {user?.email || 'admin'}</span>
                <span className="text-xs text-primary">(superadmin)</span>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={logout}
                className="glass-button text-muted-foreground hover:text-foreground"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Left Alert Feed */}
      <div className="absolute left-4 top-24 bottom-4 w-80 z-40 slide-in-left">
        <div className="glass-sidebar h-full p-4">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold text-foreground">Live Alerts</h2>
          </div>
          <LiveAlerts />
        </div>
      </div>

      {/* Right Analytics Sidebar */}
      <div className="absolute right-4 top-24 bottom-4 w-96 z-40 slide-in-right">
        <div className="glass-sidebar h-full">
          {/* System Health Section */}
          <Collapsible open={healthOpen} onOpenChange={setHealthOpen}>
            <CollapsibleTrigger className="accordion-trigger">
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-success" />
                <span className="font-semibold">System Health</span>
              </div>
              {healthOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </CollapsibleTrigger>
            <CollapsibleContent className="accordion-content">
              <div className="p-4">
                <ModuleHealthStatus />
              </div>
            </CollapsibleContent>
          </Collapsible>

          {/* Daily Event Trend Section */}
          <Collapsible open={trendsOpen} onOpenChange={setTrendsOpen}>
            <CollapsibleTrigger className="accordion-trigger">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                <span className="font-semibold">Daily Event Trend</span>
              </div>
              {trendsOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </CollapsibleTrigger>
            <CollapsibleContent className="accordion-content">
              <div className="p-4 fade-in-up">
                <AnalyticsCharts type="events-per-day" />
              </div>
            </CollapsibleContent>
          </Collapsible>

          {/* Events by Source Section */}
          <Collapsible open={modulesOpen} onOpenChange={setModulesOpen}>
            <CollapsibleTrigger className="accordion-trigger">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-accent" />
                <span className="font-semibold">Events by Source</span>
              </div>
              {modulesOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </CollapsibleTrigger>
            <CollapsibleContent className="accordion-content">
              <div className="p-4 fade-in-up">
                <AnalyticsCharts type="events-by-module" />
              </div>
            </CollapsibleContent>
          </Collapsible>

          {/* Anomaly Feed Section */}
          <Collapsible open={anomaliesOpen} onOpenChange={setAnomaliesOpen}>
            <CollapsibleTrigger className="accordion-trigger">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-warning" />
                <span className="font-semibold">Anomaly Feed</span>
              </div>
              {anomaliesOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </CollapsibleTrigger>
            <CollapsibleContent className="accordion-content">
              <div className="p-4 fade-in-up">
                <AnalyticsCharts type="anomalies" />
              </div>
            </CollapsibleContent>
          </Collapsible>
        </div>
      </div>

      {/* Global Toast Notification */}
      {showToast && lastAlert && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 neura-toast max-w-md">
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

export default Dashboard;