import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    
    @State private var email = "swayam@neuracity.dev"
    @State private var password = "password"

    var body: some View {
        ZStack {
            
            AnimatedBlobBackground()
            
            VStack(spacing: 20) {
                Spacer()
                
                Image(systemName: "shield.lefthalf.filled.badge.checkmark") // More relevant icon
                    .font(.system(size: 60))
                    .foregroundStyle(Color.neuraPrimaryGradient) // Use the gradient for the icon
                
                Text("Welcome to NeuraCity")
                    .font(.largeTitle.weight(.bold))
                    .foregroundColor(.white)
                
                Text("Your secure smart campus companion.")
                    .foregroundColor(.gray)
                
                // Use our new Frosted Glass effect for the input fields
                VStack(spacing: 1) {
                    TextField("Email", text: $email)
                        .padding()
                        .background(.clear)
                        .tint(.neuraPrimary) // Changes the color of the text cursor
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                        .textContentType(.emailAddress) // Helps with autofill

                    Divider().background(Color.white.opacity(0.2))

                    SecureField("Password", text: $password)
                        .padding()
                        .background(.clear)
                        .tint(.neuraPrimary)
                        .textContentType(.password) // Helps with autofill
                }
                .background(FrostedGlassView())
                .cornerRadius(15)
                .padding(.horizontal)

                if let errorMessage = authViewModel.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .padding(.horizontal)
                        .multilineTextAlignment(.center)
                        .transition(.opacity) // Fade the error in/out
                }
                
                Button(action: handleLogin) {
                    HStack {
                        if authViewModel.isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Text("Secure Login")
                                .fontWeight(.bold)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.neuraPrimaryGradient) // Use the new gradient
                    .foregroundColor(.white)
                    .cornerRadius(15)
                    .shadow(color: .neuraPrimary.opacity(0.3), radius: 10, y: 5) // Add a nice glow
                }
                .padding(.horizontal)
                .disabled(authViewModel.isLoading)
                // Add a scaling effect when the button is pressed
                .scaleEffect(authViewModel.isLoading ? 0.98 : 1.0)
                .animation(.spring(), value: authViewModel.isLoading)

                Spacer()
                Spacer()
            }
            .padding()
        }
    }
    
    func handleLogin() {
        Task {
           await authViewModel.login(email: email, password: password)
        }
    }
}

