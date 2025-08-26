import { AlertTriangle, Code, ExternalLink, Server } from 'lucide-react';

const CorsHelp = () => {
  return (
    <div className="neura-panel p-6 mt-4 border-warning/30">
      <div className="flex items-start gap-3 mb-4">
        <AlertTriangle className="h-5 w-5 text-warning flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-semibold text-warning mb-2">CORS Issue Detected</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Your API is running, but browsers block HTTPS → HTTP localhost requests. Here are solutions:
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <div className="neura-glass p-4 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Server className="h-4 w-4 text-primary" />
            <h4 className="font-medium text-foreground">Solution 1: Add CORS to your API</h4>
          </div>
          <p className="text-sm text-muted-foreground mb-3">
            Add these headers to your UserHub API responses:
          </p>
          <div className="bg-background/50 p-3 rounded border font-mono text-xs">
            <div>Access-Control-Allow-Origin: *</div>
            <div>Access-Control-Allow-Methods: POST, GET, OPTIONS</div>
            <div>Access-Control-Allow-Headers: Content-Type, Authorization</div>
          </div>
        </div>

        <div className="neura-glass p-4 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Code className="h-4 w-4 text-primary" />
            <h4 className="font-medium text-foreground">Solution 2: Test API directly</h4>
          </div>
          <p className="text-sm text-muted-foreground mb-2">
            Verify your API works by testing in terminal:
          </p>
          <div className="bg-background/50 p-3 rounded border font-mono text-xs">
            curl -X POST http://localhost:8005/auth/token \<br/>
            &nbsp;&nbsp;-H "Content-Type: application/x-www-form-urlencoded" \<br/>
            &nbsp;&nbsp;-d "username=alerts-system@neuracity.dev&password=a_very_strong_secret_password"
          </div>
        </div>

        <div className="neura-glass p-4 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <ExternalLink className="h-4 w-4 text-primary" />
            <h4 className="font-medium text-foreground">Solution 3: Development workaround</h4>
          </div>
          <p className="text-sm text-muted-foreground">
            For testing, you can disable CORS in Chrome: <br/>
            <code className="text-xs bg-background/50 px-1 py-0.5 rounded">
              chrome --disable-web-security --user-data-dir=/tmp/chrome_dev_test
            </code>
          </p>
        </div>
      </div>
    </div>
  );
};

export default CorsHelp;