import SwiftUI
import MapKit

struct AlertAnnotation: Identifiable {
    let id = UUID()
    let coordinate: CLLocationCoordinate2D
    let alert: Alert
}

struct MapView: View {
    @EnvironmentObject var webSocketService: WebSocketService

    // Start with a wide view of a default location (e.g., New York City)
    @State private var cameraPosition: MapCameraPosition = .region(MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 40.7128, longitude: -74.0060),
        span: MKCoordinateSpan(latitudeDelta: 0.1, longitudeDelta: 0.1)
    ))

    @State private var annotations: [AlertAnnotation] = []
    
    // The service for looking up static coordinates
    private let locationManager = LocationManager.shared

    var body: some View {
        Map(position: $cameraPosition) {
            ForEach(annotations) { annotation in
                Marker(annotation.alert.location, systemImage: "exclamationmark.triangle.fill", coordinate: annotation.coordinate)
                    .tint(.red)
            }
        }
        .preferredColorScheme(.dark)
        .ignoresSafeArea()
        .onReceive(webSocketService.$latestAlert) { newAlert in
            guard let newAlert = newAlert else { return }

            // Use the LocationManager to find coordinates for the new alert
            guard let coordinate = locationManager.getCoordinates(for: newAlert) else {
                // If no coordinates are found at all, we can't pin it.
                print("Could not find coordinates for alert at location: \(newAlert.location)")
                return
            }

            let newAnnotation = AlertAnnotation(coordinate: coordinate, alert: newAlert)
            annotations.append(newAnnotation)
            
            // Animate the map to center on the latest critical event
            withAnimation(.spring()) {
                cameraPosition = .region(MKCoordinateRegion(
                    center: coordinate,
                    span: MKCoordinateSpan(latitudeDelta: 0.01, longitudeDelta: 0.01)
                ))
            }
        }
    }
}
