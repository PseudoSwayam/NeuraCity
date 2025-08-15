# File: modules/alerts_and_notifications/utils/config.py

from utils.config_loader import settings
from modules.userhub.models import UserRole

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

# ---Role Mapping---
EVENT_TO_ROLE_MAPPING = {
    # Critical security/safety events go to security staff and administrators.
    "CV_SECURITY_ALERT":    [UserRole.security, UserRole.admin, UserRole.superadmin],
    "NLP_SECURITY_ALERT":   [UserRole.security, UserRole.admin, UserRole.superadmin],
    "IOT_SECURITY_ALERT":   [UserRole.security, UserRole.admin, UserRole.superadmin],
    "FALL_DETECTED":        [UserRole.security, UserRole.admin, UserRole.superadmin],
    "VIOLENCE_DETECTED":    [UserRole.security, UserRole.admin, UserRole.superadmin],
    "FIRE_SMOKE_DETECTED":  [UserRole.security, UserRole.admin, UserRole.superadmin],
    "INTRUSION_DETECTED":   [UserRole.security, UserRole.admin, UserRole.superadmin],
    "ABANDONED_OBJECT":     [UserRole.security, UserRole.admin, UserRole.superadmin],
    "IOT_GAS_ALERT":        [UserRole.security, UserRole.admin, UserRole.superadmin],
    "IOT_HEART_RATE_LOW":   [UserRole.staff, UserRole.admin, UserRole.superadmin],
    
    # Medium-priority health alerts can go to general staff and administrators.
    "IOT_HEART_RATE_HIGH":  [UserRole.staff, UserRole.admin, UserRole.superadmin],
    "IOT_OVERHEAT_ALERT":   [UserRole.staff, UserRole.admin, UserRole.superadmin],
    
    # General announcements should go to everyone.
    "CAMPUS_ANNOUNCEMENT":  [UserRole.student, UserRole.staff, UserRole.admin, UserRole.superadmin],
    
    # Admin notifications should only go to admins.
    "ADMIN_NOTIFICATION":   [UserRole.admin, UserRole.superadmin],
}