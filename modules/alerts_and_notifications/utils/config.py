# File: modules/alerts_and_notifications/utils/config.py

# --- Redis Configuration ---
# Must match the Redis instance your reflex_system publishes to
REDIS_HOST = "localhost"
REDIS_PORT = 6379
EVENT_CHANNEL = "campus_notifications"

# --- Webhook Channel Configuration ---
# A dummy URL for now. Use a service like webhook.site to test this.
# This will be the endpoint for your future push notification service.
WEBHOOK_URL = "https://webhook.site/adb60c2d-1eec-4edf-9eaa-5600bd8bc563"

# --- Notification Templates ---
# Simple string templates to format messages for different event types
MESSAGE_TEMPLATES = {
    # --- ADDED: Specific templates for different security alert sources ---
    "CV_SECURITY_ALERT": "🚨 CRITICAL SECURITY ALERT: The Watchtower AI has detected an urgent situation at {location}. A security team has been dispatched immediately.",
    "NLP_SECURITY_ALERT": "🚨 SECURITY ALERT: A user has requested a security dispatch to the following location: {location}.",
    "SECURITY_ALERT": "🚨 A generic security alert was triggered for {location}.",
    "FALL_DETECTED": "❗ FALL DETECTED at {location}. Immediate assistance may be required.",
    "VIOLENCE_DETECTED": "⚠️ VIOLENCE DETECTED at {location}. Reason: {reason}.",
    "FIRE_SMOKE_DETECTED": "🔥 FIRE/SMOKE DETECTED at {location}. Activating fire response protocol.",
    "ABANDONED_OBJECT": "👜 Unattended object detected at {location} for over {duration} seconds. Please investigate.",
    "INTRUSION_DETECTED": "🚫 Intrusion detected in a restricted zone at {location}.",
    "ADMIN_NOTIFICATION": "🔔 ADMIN NOTIFICATION for {department}: {message}",
    "DEFAULT": "ℹ️ An unclassified event '{event_type}' was triggered by source '{triggered_by}'."
}