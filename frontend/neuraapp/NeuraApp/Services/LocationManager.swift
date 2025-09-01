//
//  LocationManager.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import Foundation
import CoreLocation

class LocationManager {
    static let shared = LocationManager()
    
    // This dictionary holds your manually defined static coordinates for known locations.
    // The key MUST EXACTLY match the "camera_id" received in the alert's payload.
    private let staticLocations: [String: CLLocationCoordinate2D] = [
        "LobbyCam-01": CLLocationCoordinate2D(latitude: 40.7135, longitude: -74.0066),
        "Fall Cam": CLLocationCoordinate2D(latitude: 40.7135, longitude: -74.0066),
        "Courtyard-01": CLLocationCoordinate2D(latitude: 40.7145, longitude: -74.0055),
        "Loitering Cam": CLLocationCoordinate2D(latitude: 40.7145, longitude: -74.0055),
        "Plaza-01": CLLocationCoordinate2D(latitude: 40.7125, longitude: -74.0045),
        "Abandoned Bag Cam": CLLocationCoordinate2D(latitude: 40.7125, longitude: -74.0045),
        "Alley-01": CLLocationCoordinate2D(latitude: 40.7130, longitude: -74.0080),
        "Fight Cam": CLLocationCoordinate2D(latitude: 40.7130, longitude: -74.0080),
        "Lab-01": CLLocationCoordinate2D(latitude: 40.7150, longitude: -74.0070),
        "Fire Cam": CLLocationCoordinate2D(latitude: 40.7150, longitude: -74.0070),
        "Entrance-01": CLLocationCoordinate2D(latitude: 40.7138, longitude: -74.0040),
        "Normal Activity Cam": CLLocationCoordinate2D(latitude: 40.7138, longitude: -74.0040),
        "Main Gate": CLLocationCoordinate2D(latitude: 40.7130, longitude: -74.0035),
        "Main Library": CLLocationCoordinate2D(latitude: 40.7128, longitude: -74.0075),
        "Iot_pulsenet-01": CLLocationCoordinate2D(latitude: 40.7140, longitude: -74.0060)
        // Add more known camera locations and their coordinates here...
    ]
    
    /// Looks up coordinates for an alert.
    /// It first checks if the alert payload itself contains coordinates.
    /// If not, it falls back to the static dictionary using the camera_id as a key.
    func getCoordinates(for alert: Alert) -> CLLocationCoordinate2D? {
        // 1. Prioritize live coordinates if they exist in the payload
        if let liveCoordinates = alert.coordinates {
            return liveCoordinates
        }
        
        // 2. Fallback to the static dictionary using the camera ID
        if let cameraId = alert.rawEventData.payload.cameraId,
           let staticCoordinates = staticLocations[cameraId] {
            return staticCoordinates
        }
        
        // 3. If no match is found, return nil
        return nil
    }
}
