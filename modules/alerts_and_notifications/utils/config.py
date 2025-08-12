# File: modules/alerts_and_notifications/utils/config.py

from utils.config_loader import settings

# The Webhook URL can be centrally managed now
WEBHOOK_URL = settings.WEBHOOK_URL

# --- Notification Templates ---
MESSAGE_TEMPLATES = {   
    "CV_SECURITY_ALERT": "🚨 CRITICAL SECURITY ALERT: The Watchtower AI has detected an urgent situation at {location}. A security team has been dispatched immediately.",
    "NLP_SECURITY_ALERT": "🚨 SECURITY ALERT: A user has requested a security dispatch to the following location: {location}.",
    "SECURITY_ALERT": "🚨 A generic security alert was triggered for {location}.",
    "FALL_DETECTED": "❗ FALL DETECTED at {location}. Immediate assistance may be required.",
    "VIOLENCE_DETECTED": "⚠️ VIOLENCE DETECTED at {location}. Reason: {reason}.",
    "FIRE_SMOKE_DETECTED": "🔥 FIRE/SMOKE DETECTED at {location}. Activating fire response protocol.",
    "ABANDONED_OBJECT": "👜 Unattended object detected at {location} for over {duration} seconds. Please investigate.",
    "INTRUSION_DETECTED": "🚫 Intrusion detected in a restricted zone at {location}.",
    "CAMPUS_ANNOUNCEMENT": "📢 CAMPUS-WIDE ANNOUNCEMENT (from {triggered_by}): {message}",
    "ADMIN_NOTIFICATION": "🔔 ADMIN NOTIFICATION for {department}: {message}",
    "DEFAULT": "ℹ️ An unclassified event '{event_type}' was triggered by source '{triggered_by}'."
}