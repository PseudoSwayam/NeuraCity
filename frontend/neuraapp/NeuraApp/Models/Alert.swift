import Foundation
import CoreLocation

// Top-level alert struct, this part is okay.
struct Alert: Decodable, Identifiable {
    let id = UUID()
    let humanReadableMessage: String
    let rawEventData: RawEventData

    enum CodingKeys: String, CodingKey {
        case humanReadableMessage = "human_readable_message"
        case rawEventData = "raw_event_data"
    }

    // Convenience properties to make accessing data easy
    var location: String { rawEventData.payload.location }
    var timestamp: Date { rawEventData.payload.timestamp }
    var eventType: String { rawEventData.eventType }
    var coordinates: CLLocationCoordinate2D? {
        rawEventData.payload.coordinates?.coordinate2D
    }
}

// RawEventData struct, this part is okay.
struct RawEventData: Decodable {
    let eventType: String
    let payload: AlertPayload
    
    enum CodingKeys: String, CodingKey {
        case eventType = "event_type"
        case payload
    }
}

struct AlertPayload: Decodable {
    let location: String
    let cameraId: String?
    let timestamp: Date
    let coordinates: Coordinates?

    // Custom Coding Keys to map from snake_case JSON
    enum CodingKeys: String, CodingKey {
        case location
        case cameraId = "camera_id"
        case timestamp, coordinates
    }

    // The new, fully robust custom initializer.
    // This replaces the struct's default Codable behavior.
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        // These fields are required. If they are missing, it's a real error.
        self.location = try container.decode(String.self, forKey: .location)
        self.timestamp = try container.decode(Date.self, forKey: .timestamp)
        
        // These fields are optional. We use 'decodeIfPresent'.
        // This will succeed if the key is missing OR if the value is null.
        // THIS IS THE CORE OF THE FIX.
        self.cameraId = try container.decodeIfPresent(String.self, forKey: .cameraId)
        self.coordinates = try container.decodeIfPresent(Coordinates.self, forKey: .coordinates)
    }
}

struct Coordinates: Decodable {
    let latitude: Double
    let longitude: Double

    // Helper property remains the same
    var coordinate2D: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }
}
