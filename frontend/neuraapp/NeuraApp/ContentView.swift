//
//  ContentView.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import SwiftUI

struct ContentView: View {
    // Access the shared AuthViewModel from the environment.
    @EnvironmentObject var authViewModel: AuthViewModel
    
    var body: some View {
        ZStack {
            // Set a global background color for the entire app.
            Color.neuraBackground.ignoresSafeArea()

            if authViewModel.isAuthenticated {
                // If logged in, show the main tab bar view.
                MainTabView()
            } else {
                // Otherwise, show the login view.
                LoginView()
            }
        }
    }
}
