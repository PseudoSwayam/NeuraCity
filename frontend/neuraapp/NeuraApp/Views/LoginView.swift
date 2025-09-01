//
//  LoginView.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    
    @State private var email = "swayam@neuracity.dev"
    @State private var password = "password"

    var body: some View {
        VStack(spacing: 20) {
            Spacer()
            
            // Logo and Title
            Image(systemName: "shield.lefthalf.filled") // Using SF Symbols as a placeholder
                .font(.system(size: 60))
                .foregroundColor(.neuraPrimary)
            
            Text("Welcome to NeuraCity")
                .font(.largeTitle)
                .fontWeight(.bold)
                .foregroundColor(.white)
            
            Text("Your secure smart campus companion.")
                .foregroundColor(.gray)
            
            // Form Fields
            VStack(spacing: 15) {
                TextField("Email", text: $email)
                    .padding()
                    .background(Color.neuraSurface)
                    .cornerRadius(10)
                    .keyboardType(.emailAddress)
                    .autocapitalization(.none)

                SecureField("Password", text: $password)
                    .padding()
                    .background(Color.neuraSurface)
                    .cornerRadius(10)
            }
            .padding(.horizontal)
            
            // Error Message Display
            if let errorMessage = authViewModel.errorMessage {
                Text(errorMessage)
                    .foregroundColor(.red)
                    .padding(.horizontal)
                    .multilineTextAlignment(.center)
            }
            
            // Login Button with Loading Indicator
            Button(action: {
                Task {
                   await authViewModel.login(email: email, password: password)
                }
            }) {
                HStack {
                    if authViewModel.isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .black))
                    } else {
                        Text("Secure Login")
                            .fontWeight(.bold)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.neuraPrimary)
                .foregroundColor(.black)
                .cornerRadius(10)
            }
            .padding(.horizontal)
            .disabled(authViewModel.isLoading) // Disable button while loading

            Spacer()
            Spacer()
        }
        .padding()
        .background(Color.neuraBackground)
        .edgesIgnoringSafeArea(.all)
    }
}
