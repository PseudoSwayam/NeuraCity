//
//  MapView.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import SwiftUI
import MapKit

// An identifiable annotation for placing on the map
struct AlertAnnotation: Identifiable {
    let id = UUID()
    let coordinate: CLLocationCoordinate2D
    let alert: Alert
}

struct MapView: View {
    @EnvironmentObject var webSocketService: WebSocketService

    // This state variable holds the map's current camera position.
    @State private var cameraPosition: MapCameraPosition = .automatic

    // A list of annotations (pins) to display on the map.
    @State private var annotations: [AlertAnnotation] = []

    var body: some View {
        Map(position: $cameraPosition) {
            // Loop through our annotations and create a Marker for each.
            ForEach(annotations) { annotation in
                Marker(annotation.alert.location, systemImage: "exclamationmark.triangle.fill", coordinate: annotation.coordinate)
                    .tint(.red)
            }
        }
        // Use the preferred dark color scheme for the map tiles
        .preferredColorScheme(.dark)
        .ignoresSafeArea()
        // Listen for new alerts from our WebSocket service
        .onReceive(webSocketService.$latestAlert) { newAlert in
            guard let newAlert = newAlert, let coordinate = newAlert.coordinates else { return }

            let newAnnotation = AlertAnnotation(coordinate: coordinate, alert: newAlert)
            annotations.append(newAnnotation)
            
            // When a new alert arrives, automatically animate the map to its location.
            withAnimation(.easeInOut(duration: 1.0)) {
                cameraPosition = .region(MKCoordinateRegion(
                    center: coordinate,
                    span: MKCoordinateSpan(latitudeDelta: 0.01, longitudeDelta: 0.01)
                ))
            }
        }
    }
}
