//
//  ChatView.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import SwiftUI

struct ChatView: View {
    // Create an instance of the view model specific to this view.
    @StateObject private var viewModel = ChatViewModel()
    @State private var messageText: String = ""

    var body: some View {
        VStack {
            // Conversation History
            ScrollView {
                VStack {
                    ForEach(viewModel.messages) { message in
                        MessageView(message: message)
                    }
                    if viewModel.isThinking {
                        MessageView(message: ChatMessage(text: "", author: .agent, isLoading: true))
                    }
                }
            }
            
            // Text Input Field
            HStack {
                TextField("Ask NeuraNLP...", text: $messageText)
                    .padding()
                    .background(Color.neuraSurface)
                    .cornerRadius(10)

                Button(action: sendMessage) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.largeTitle)
                        .foregroundColor(.neuraPrimary)
                }
            }
            .padding()
        }
        .background(Color.neuraBackground)
    }
    
    func sendMessage() {
        guard !messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        let tempMessage = messageText
        messageText = ""
        Task {
            await viewModel.sendMessage(tempMessage)
        }
    }
}

// A sub-view for a single chat bubble
struct MessageView: View {
    let message: ChatMessage
    
    var body: some View {
        HStack {
            if message.author == .user {
                Spacer()
            }
            
            if message.isLoading {
                // "Thinking" indicator
                HStack(spacing: 4) {
                    Circle().frame(width: 8, height: 8).opacity(0.5)
                    Circle().frame(width: 8, height: 8).opacity(0.8)
                    Circle().frame(width: 8, height: 8)
                }
                .padding()
                .background(Color.neuraSurface)
                .cornerRadius(16)
            } else {
                Text(message.text)
                    .padding()
                    .foregroundColor(.white)
                    .background(message.author == .user ? Color.neuraPrimary : Color.neuraSurface)
                    .cornerRadius(16)
            }

            if message.author == .agent {
                Spacer()
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 4)
    }
}
