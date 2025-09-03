import SwiftUI

// This new structure uses a simple ScrollView directly inside the background ZStack.
// It avoids the complex List and NavigationView background conflicts.
struct HomeView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    
    var body: some View {
        ZStack {
            // Layer 1: The animated background. It's always here.
            AnimatedBlobBackground()

            // Layer 2: The scrollable content.
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    // This creates padding at the top to avoid the notch.
                    Color.clear.frame(height: 70)
                    
                    // Main UI content
                    HeaderView()
                    AttendanceCard()
                    AlertsView()
                }
                .padding()
            }
        }
        .ignoresSafeArea()
    }
}


// --- SUB-VIEWS FOR HOMEVIEW ---
// We've broken down the HomeView into more modular pieces for clarity and stability.

// This view contains the "Dashboard" title and the logout button.
struct HeaderView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    
    var body: some View {
        HStack {
            Text("Dashboard")
                .font(.largeTitle.weight(.bold))
                .foregroundColor(.white)
            
            Spacer()
            
            Button(action: { authViewModel.logout() }) {
                Image(systemName: "rectangle.portrait.and.arrow.right")
                    .foregroundColor(.white)
                    .font(.title2)
            }
        }
        .overlay(WelcomeHeader(), alignment: .bottomLeading)
    }
}

// WelcomeHeader now correctly uses a task.
struct WelcomeHeader: View {
    @State private var userName: String = ""
    var body: some View {
        // We add an empty Text view to ensure this view can be correctly overlaid.
        // It provides the layout structure.
        Text(userName.isEmpty ? "" : "Welcome back, \(userName)")
            .font(.subheadline)
            .foregroundColor(.gray)
            .padding(.top, 50)
            .task { await loadUserData() }
    }
    
    private func loadUserData() async {
        do {
            let user = try await ApiService.shared.getMyProfile()
            self.userName = user.fullName
        } catch { self.userName = "User" }
    }
}


// AttendanceCard remains the same, but will now render correctly.
struct AttendanceCard: View {
    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: "figure.walk.arrival")
                .font(.title)
                .foregroundColor(.neuraAccent)
            VStack(alignment: .leading) {
                Text("Last Activity").fontWeight(.semibold)
                Text("Checked In at Main Entrance").foregroundColor(.gray)
            }
            Spacer()
        }
        .padding()
        .background(FrostedGlassView())
        .cornerRadius(15)
        .overlay(RoundedRectangle(cornerRadius: 15).stroke(Color.white.opacity(0.1)))
    }
}

// The new combined AlertsView that receives the WebSocket data directly.
struct AlertsView: View {
    @EnvironmentObject var webSocketService: WebSocketService
    @State private var alerts: [Alert] = []

    var body: some View {
        VStack(alignment: .leading) {
            Text("Live Campus Alerts")
                .font(.title2.weight(.bold))
                .foregroundColor(.white)
                .padding(.horizontal)
            
            // This is now a simple, non-scrolling VStack. The parent view handles scrolling.
            VStack(spacing: 0) {
                if alerts.isEmpty {
                    EmptyAlertsView()
                } else {
                    ForEach(alerts.prefix(10)) { alert in
                        AlertRow(alert: alert)
                    }
                }
            }
            .padding(.top, 8)
        }
        .padding(.vertical)
        .background(FrostedGlassView())
        .cornerRadius(20)
        .overlay(RoundedRectangle(cornerRadius: 20).stroke(Color.white.opacity(0.1)))
        // This is where we now listen for the WebSocket data.
        .onReceive(webSocketService.$latestAlert) { newAlert in
            guard let newAlert = newAlert else { return }
            withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) {
                alerts.insert(newAlert, at: 0)
            }
        }
    }
}

struct EmptyAlertsView: View {
    var body: some View {
        VStack {
            Image(systemName: "checkmark.shield.fill")
                .font(.largeTitle).foregroundColor(.green)
            Text("No recent alerts.").fontWeight(.semibold)
            Text("The campus is secure.").foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity, alignment: .center).padding(.vertical, 50)
    }
}

struct AlertRow: View {
    let alert: Alert
    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: "bell.and.waveform.fill")
                .font(.title2)
                .foregroundColor(alert.eventType == "CV_SECURITY_ALERT" ? .red : .yellow)
            VStack(alignment: .leading) {
                Text(alert.location).fontWeight(.semibold)
                Text(alert.humanReadableMessage)
                    .font(.caption).foregroundColor(.gray).lineLimit(2)
            }
            Spacer()
            Text(alert.timestamp, style: .time)
                .font(.subheadline.monospacedDigit()).foregroundColor(.gray)
        }
        .padding()
        .overlay(Divider().padding(.horizontal).opacity(0.3), alignment: .bottom)
        .transition(.asymmetric(insertion: .move(edge: .top).combined(with: .opacity), removal: .scale.combined(with: .opacity)))
    }
}
