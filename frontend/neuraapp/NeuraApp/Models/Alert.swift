//
//  Alert.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import Foundation
import CoreLocation // We use this for geographic coordinates

// This represents the entire alert message received from the WebSocket.
struct Alert: Codable, Identifiable {
    let id = UUID() // Make it uniquely identifiable for SwiftUI lists
    let humanReadableMessage: String
    let rawEventData: RawEventData

    // We add CodingKeys to handle snake_case from the JSON
    enum CodingKeys: String, CodingKey {
        case humanReadableMessage = "human_readable_message"
        case rawEventData = "raw_event_data"
    }
    
    // For convenience, we can create computed properties to easily access nested data
    var location: String { rawEventData.payload.location }
    var timestamp: Date { rawEventData.payload.timestamp }
    var eventType: String { rawEventData.eventType }
    var coordinates: CLLocationCoordinate2D? {
        guard let coords = rawEventData.payload.coordinates else { return nil }
        return CLLocationCoordinate2D(latitude: coords.latitude, longitude: coords.longitude)
    }
}

struct RawEventData: Codable {
    let eventType: String
    let payload: AlertPayload
    
    enum CodingKeys: String, CodingKey {
        case eventType = "event_type"
        case payload
    }
}

struct AlertPayload: Codable {
    let location: String
    let cameraId: String
    let timestamp: Date // Swift's JSONDecoder can automatically handle ISO 8601 date strings
    let coordinates: Coordinates?

    enum CodingKeys: String, CodingKey {
        case location
        case cameraId = "camera_id"
        case timestamp, coordinates
    }
}

struct Coordinates: Codable {
    let latitude: Double
    let longitude: Double
}
