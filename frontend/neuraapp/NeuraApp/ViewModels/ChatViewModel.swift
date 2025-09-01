//
//  ChatViewModel.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import Foundation

@MainActor
class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var isThinking: Bool = false
    
    private let apiService = ApiService.shared

    func sendMessage(_ text: String) async {
        // Add the user's message to the chat list immediately.
        messages.append(ChatMessage(text: text, author: .user))
        
        isThinking = true
        
        do {
            let responseText = try await apiService.submitQuery(text)
            let agentMessage = ChatMessage(text: responseText, author: .agent)
            messages.append(agentMessage)
        } catch {
            // Handle errors by showing an error message in the chat.
            let errorMessage = ChatMessage(text: "Sorry, I encountered an error. Please try again.", author: .agent)
            messages.append(errorMessage)
        }
        
        isThinking = false
    }
}
