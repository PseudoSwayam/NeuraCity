//
//  NeuraAppApp.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import SwiftUI

@main
struct NeuraAppApp: App {
    // We create an instance of our AuthViewModel here and share it across the whole app.
    @StateObject private var authViewModel = AuthViewModel()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authViewModel) // Pass the view model into the environment.
        }
    }
}
