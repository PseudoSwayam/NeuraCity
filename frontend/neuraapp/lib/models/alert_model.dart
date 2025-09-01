import 'package:latlong2/latlong.dart'; // This import is correct. The error was in its usage.

class Alert {
  final String humanReadableMessage;
  final String eventType;
  final String location;
  final String cameraId;
  final DateTime timestamp;
  final LatLng? coordinates; // Can be null if the alert payload doesn't contain coordinates.

  Alert({
    required this.humanReadableMessage,
    required this.eventType,
    required this.location,
    required this.cameraId,
    required this.timestamp,
    this.coordinates,
  });

  factory Alert.fromJson(Map<String, dynamic> json) {
    final rawData = json['raw_event_data'] as Map<String, dynamic>? ?? {};
    final payload = rawData['payload'] as Map<String, dynamic>? ?? {};
    
    // CHANGED: Correctly parse the nested coordinates object from the new payload.
    LatLng? parsedCoordinates;
    if (payload.containsKey('coordinates')) {
      final coordsData = payload['coordinates'] as Map<String, dynamic>?;
      if (coordsData != null &&
          coordsData.containsKey('latitude') &&
          coordsData.containsKey('longitude')) {
        parsedCoordinates = LatLng(
          (coordsData['latitude'] as num).toDouble(),
          (coordsData['longitude'] as num).toDouble(),
        );
      }
    }

    return Alert(
      humanReadableMessage: json['human_readable_message'] ?? 'Alert message not available.',
      eventType: rawData['event_type'] ?? 'UNKNOWN_EVENT',
      location: payload['location'] ?? 'Unknown Location',
      cameraId: payload['camera_id'] ?? 'N/A',
      timestamp: DateTime.tryParse(payload['timestamp'] ?? '') ?? DateTime.now(),
      coordinates: parsedCoordinates, // Assign the correctly parsed value here.
    );
  }
}