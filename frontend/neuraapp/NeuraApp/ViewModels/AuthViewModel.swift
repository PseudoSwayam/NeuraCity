//
//  AuthViewModel.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import Foundation
import SwiftUI

// An ObservableObject is a class that can publish its changes, so the UI can update.
@MainActor // This ensures that UI-related updates happen on the main thread.
class AuthViewModel: ObservableObject {
    
    // @Published properties automatically announce when they change.
    @Published var isAuthenticated: Bool = false
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // Dependencies
    private let apiService = ApiService.shared
    private let keychainService = KeychainService.shared
    
    init() {
        // Check if a token already exists when the app starts.
        checkToken()
    }
    
    func checkToken() {
        if keychainService.getToken() != nil {
            isAuthenticated = true
        } else {
            isAuthenticated = false
        }
    }
    
    func login(email: String, password: String) async {
        isLoading = true
        errorMessage = nil
        
        do {
            // 1. Call the API service to get a token.
            let token = try await apiService.login(email: email, password: password)
            // 2. Securely save the token.
            keychainService.saveToken(token)
            
            // 3. Get user profile to perform check-in.
            let user = try await apiService.getMyProfile()
            try await apiService.performCheckIn(forUser: user)

            // 4. Update the UI state.
            isAuthenticated = true
        } catch let error as APIError {
            errorMessage = error.localizedDescription
        } catch {
            errorMessage = "An unexpected error occurred."
        }
        
        isLoading = false
    }
    
    func logout() {
        keychainService.deleteToken()
        isAuthenticated = false
    }
}
