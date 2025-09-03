import SwiftUI

struct HomeView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @EnvironmentObject var webSocketService: WebSocketService

    @State private var alerts: [Alert] = []
    
    var body: some View {
        // We use a ZStack to layer the background gradient behind our content
        ZStack {
            RadialGradient(gradient: Gradient(colors: [.neuraSurface, .neuraBackground]), center: .topLeading, startRadius: 5, endRadius: 900)
                .ignoresSafeArea()

            NavigationView {
                // Main content is now in a VStack instead of a ScrollView,
                // because our alerts panel will handle its own scrolling.
                VStack(alignment: .leading, spacing: 24) {
                    WelcomeHeader()
                    AttendanceCard()
                    // The alerts section is now a fixed-height, scrollable panel.
                    LiveAlertsPanel(alerts: alerts)
                }
                .padding()
                .navigationTitle("Dashboard")
                .background(.clear) // Let the ZStack's gradient show through
                .toolbar {
                    ToolbarItem(placement: .navigationBarTrailing) {
                        Button(action: {
                            authViewModel.logout()
                        }) {
                            Image(systemName: "rectangle.portrait.and.arrow.right")
                        }
                    }
                }
            }
            // Use .task for modern, safe view appearance logic
            .task {
                setupNavigationBarAppearance()
            }
            .onReceive(webSocketService.$latestAlert) { newAlert in
                guard let newAlert = newAlert else { return }
                // Use a spring animation for a bouncy, delightful effect when a new alert arrives
                withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) {
                    alerts.insert(newAlert, at: 0)
                }
            }
        }
    }
    
    private func setupNavigationBarAppearance() {
        let appearance = UINavigationBarAppearance()
        // Make navigation bar transparent to show the gradient behind
        appearance.configureWithTransparentBackground()
        appearance.largeTitleTextAttributes = [.foregroundColor: UIColor.white]
        appearance.titleTextAttributes = [.foregroundColor: UIColor.white]
        UINavigationBar.appearance().standardAppearance = appearance
        UINavigationBar.appearance().scrollEdgeAppearance = appearance
        UINavigationBar.appearance().compactAppearance = appearance
    }
}

// --- SUB-VIEWS FOR HOMEVIEW ---

struct WelcomeHeader: View {
    @State private var userName: String = "..."

    var body: some View {
        VStack(alignment: .leading) {
            Text("Welcome back,")
                .font(.subheadline)
                .foregroundColor(.gray)
            Text(userName)
                .font(.largeTitle.weight(.bold))
        }
        .task { await loadUserData() }
    }
    
    private func loadUserData() async {
        do {
            let user = try await ApiService.shared.getMyProfile()
            self.userName = user.fullName
        } catch { self.userName = "User" }
    }
}

struct AttendanceCard: View {
    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: "figure.walk.arrival") // Better icon
                .font(.title)
                .foregroundColor(.neuraAccent)
            VStack(alignment: .leading) {
                Text("Last Activity").fontWeight(.semibold)
                Text("Checked In at Main Entrance").foregroundColor(.gray)
            }
            Spacer()
        }
        .padding()
        .background(FrostedGlassView()) // Use the new glass effect!
        .cornerRadius(15)
        .overlay(RoundedRectangle(cornerRadius: 15).stroke(Color.white.opacity(0.1))) // Subtle border
    }
}

// THIS IS THE NEW SCROLLABLE PANEL
struct LiveAlertsPanel: View {
    let alerts: [Alert]
    
    var body: some View {
        VStack(alignment: .leading) {
            Text("Live Campus Alerts")
                .font(.title2).fontWeight(.bold)
                .padding(.horizontal)
            
            // A ScrollView that contains our list of alerts.
            // This makes the panel itself scrollable, independent of the main screen.
            ScrollView {
                if alerts.isEmpty {
                    VStack {
                        Image(systemName: "checkmark.shield.fill")
                            .font(.largeTitle)
                            .foregroundColor(.green)
                        Text("No recent alerts.")
                            .fontWeight(.semibold)
                        Text("The campus is secure.")
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding(.vertical, 50)
                } else {
                    LazyVStack(spacing: 0) { // LazyVStack is efficient for long lists
                        ForEach(alerts) { alert in
                            AlertRow(alert: alert)
                        }
                    }
                }
            }
            .padding(.top, 8)
        }
        .padding(.vertical)
        .background(FrostedGlassView())
        .cornerRadius(20)
        .overlay(RoundedRectangle(cornerRadius: 20).stroke(Color.white.opacity(0.1)))
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
                    .font(.caption)
                    .foregroundColor(.gray)
                    .lineLimit(2)
            }
            Spacer()
            Text(alert.timestamp, style: .time)
                .font(.subheadline.monospacedDigit())
                .foregroundColor(.gray)
        }
        .padding()
        // Add a nice dividing line between alerts
        .overlay(Divider().padding(.horizontal).opacity(0.3), alignment: .bottom)
        .transition(.asymmetric(insertion: .move(edge: .top).combined(with: .opacity), removal: .scale.combined(with: .opacity)))
    }
}
