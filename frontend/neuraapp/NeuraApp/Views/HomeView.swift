import SwiftUI

struct HomeView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @EnvironmentObject var webSocketService: WebSocketService

    @State private var alerts: [Alert] = []
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    WelcomeHeader()
                    AttendanceCard()
                    LiveAlertsSection(alerts: alerts)
                }
                .padding()
            }
            .navigationTitle("Dashboard")
            .background(Color.neuraBackground)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        authViewModel.logout()
                    }) {
                        Image(systemName: "rectangle.portrait.and.arrow.right")
                    }
                }
            }
            // Use dark navigation bar style throughout the app
            .navigationBarTitleDisplayMode(.large)
        }
        .onAppear {
            // Apply a consistent dark theme to the navigation bar
            let appearance = UINavigationBarAppearance()
            appearance.configureWithOpaqueBackground()
            appearance.backgroundColor = UIColor(Color.neuraBackground)
            appearance.largeTitleTextAttributes = [.foregroundColor: UIColor.white]
            appearance.titleTextAttributes = [.foregroundColor: UIColor.white]
            UINavigationBar.appearance().standardAppearance = appearance
            UINavigationBar.appearance().scrollEdgeAppearance = appearance
            UINavigationBar.appearance().compactAppearance = appearance
        }
        .onReceive(webSocketService.$latestAlert) { newAlert in
            guard let newAlert = newAlert else { return }
            // Add the new alert to the top of our list with an animation
            withAnimation {
                alerts.insert(newAlert, at: 0)
            }
        }
    }
}

// --- Sub-views for HomeView (Complete and Correct) ---

struct WelcomeHeader: View {
    @State private var userName: String = "..."

    var body: some View {
        VStack(alignment: .leading) {
            Text("Welcome back,")
                .font(.subheadline)
                .foregroundColor(.gray)
            Text(userName)
                .font(.largeTitle)
                .fontWeight(.bold)
        }
        .task { // Use .task for modern, safe async operations in SwiftUI
            await loadUserData()
        }
    }
    
    private func loadUserData() async {
        do {
            let user = try await ApiService.shared.getMyProfile()
            self.userName = user.fullName
        } catch {
            self.userName = "User"
        }
    }
}

struct AttendanceCard: View {
    var body: some View {
        HStack {
            Image(systemName: "location.fill")
                .foregroundColor(.neuraAccent)
            VStack(alignment: .leading) {
                Text("Last Activity").fontWeight(.semibold)
                Text("Checked In at Main Entrance").foregroundColor(.gray)
            }
            Spacer()
        }
        .padding()
        .background(Color.neuraSurface)
        .cornerRadius(12)
    }
}

struct LiveAlertsSection: View {
    let alerts: [Alert]
    
    var body: some View {
        VStack(alignment: .leading) {
            Text("Live Campus Alerts")
                .font(.title2).fontWeight(.bold)
            
            if alerts.isEmpty {
                Text("No recent alerts. Campus is secure.")
                    .foregroundColor(.gray)
                    .padding()
                    .frame(maxWidth: .infinity, minHeight: 100)
                    .background(Color.neuraSurface)
                    .cornerRadius(12)
            } else {
                // Display up to the 5 most recent alerts
                ForEach(alerts.prefix(5)) { alert in
                    AlertRow(alert: alert)
                }
            }
        }
    }
}

struct AlertRow: View {
    let alert: Alert

    var body: some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.yellow)
            VStack(alignment: .leading) {
                Text(alert.location).fontWeight(.semibold)
                Text(alert.humanReadableMessage)
                    .font(.caption)
                    .foregroundColor(.gray)
                    .lineLimit(2)
            }
            Spacer()
            Text(alert.timestamp, style: .time)
                .font(.caption)
                .foregroundColor(.gray)
        }
        .padding()
        .background(alert.eventType == "CV_SECURITY_ALERT" ? Color.red.opacity(0.2) : Color.neuraSurface)
        .cornerRadius(12)
        .transition(.asymmetric(insertion: .move(edge: .top).combined(with: .opacity), removal: .scale))
    }
}
