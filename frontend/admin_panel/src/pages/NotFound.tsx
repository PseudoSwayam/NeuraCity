import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { AlertTriangle, ArrowLeft, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-destructive/5" />
      
      {/* Floating Orbs */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-destructive/10 rounded-full blur-3xl neura-float" />
      <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-warning/10 rounded-full blur-3xl neura-float" style={{ animationDelay: '-3s' }} />

      {/* Error Content */}
      <div className="neura-panel p-8 text-center max-w-md mx-4 neura-glow">
        <div className="mb-6">
          <AlertTriangle className="h-16 w-16 text-destructive mx-auto mb-4 neura-pulse" />
          <h1 className="text-6xl font-bold text-destructive mb-2">404</h1>
          <h2 className="text-xl font-semibold text-foreground mb-2">
            Access Denied
          </h2>
          <p className="text-muted-foreground">
            The requested neural pathway could not be found in the NeuraCity network.
          </p>
        </div>

        <div className="space-y-3">
          <Button 
            onClick={() => window.location.href = "/"} 
            className="w-full bg-gradient-primary hover:shadow-neura-intense transition-neura text-primary-foreground"
          >
            <Home className="h-4 w-4 mr-2" />
            Return to Command Center
          </Button>
          
          <Button 
            variant="outline" 
            onClick={() => window.history.back()}
            className="w-full neura-glass border-primary/30 hover:border-primary"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go Back
          </Button>
        </div>

        <div className="mt-6 text-xs text-muted-foreground">
          <p>Error Code: NEURAL_PATH_NOT_FOUND</p>
          <p className="mt-1">Timestamp: {new Date().toISOString()}</p>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
