//
//  Alert.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import Foundation
import CoreLocation

struct Alert: Codable, Identifiable {
    let id = UUID()
    let humanReadableMessage: String
    let rawEventData: RawEventData

    enum CodingKeys: String, CodingKey {
        case humanReadableMessage = "human_readable_message"
        case rawEventData = "raw_event_data"
    }

    // Convenience properties to easily access the important, cleaned data
    var location: String { rawEventData.payload.location }
    var timestamp: Date { rawEventData.payload.timestamp }
    var eventType: String { rawEventData.eventType }
    var coordinates: CLLocationCoordinate2D? { rawEventData.payload.coordinates?.coordinate2D }
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
    let cameraId: String? // Optional to prevent crashes if it's missing
    let timestamp: Date
    let coordinates: Coordinates? // Optional to prevent crashes if it's missing or null

    enum CodingKeys: String, CodingKey {
        case location
        case cameraId = "camera_id"
        case timestamp, coordinates
    }
}

struct Coordinates: Codable {
    let latitude: Double
    let longitude: Double

    // Helper property to easily convert to the format MapKit needs
    var coordinate2D: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }
}
