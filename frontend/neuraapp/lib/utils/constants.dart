class AppConstants {
  // IMPORTANT: Replace with your server's local IP address.
  // To find it on a Mac: System Settings > Wi-Fi > Details > TCP/IP. Look for "IP Address".
  // Your computer and your phone/simulator must be on the same Wi-Fi network.
  static const String serverIP = "192.168.0.180"; // <--- CHANGE THIS

  static const String userHubBaseUrl = "http://$serverIP:8005";
  static const String nlpAgentBaseUrl = "http://$serverIP:8000";
  static const String alertsWebSocketUrl = "ws://$serverIP:8003/ws/alerts";
}