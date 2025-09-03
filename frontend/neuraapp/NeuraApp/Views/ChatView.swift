//
//  ChatView.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import SwiftUI

struct ChatView: View {
    @StateObject private var viewModel = ChatViewModel()
    @State private var messageText: String = ""

    var body: some View {
        VStack {
            // Conversation History
            ScrollViewReader { scrollViewProxy in
                ScrollView {
                    VStack(spacing: 12) {
                        ForEach(viewModel.messages) { message in
                            MessageView(message: message)
                                .id(message.id) // Assign an ID to each message
                        }
                        if viewModel.isThinking {
                            MessageView(message: ChatMessage(text: "", author: .agent, isLoading: true))
                        }
                    }
                    .padding(.top)
                }
                // When new messages are added, automatically scroll to the bottom
                .onChange(of: viewModel.messages.count) { _ in
                    if let lastMessageId = viewModel.messages.last?.id {
                        withAnimation {
                            scrollViewProxy.scrollTo(lastMessageId, anchor: .bottom)
                        }
                    }
                }
            }
            
            // Text Input Field
            HStack(spacing: 16) {
                TextField("Ask NeuraNLP...", text: $messageText, onCommit: sendMessage)
                    .padding()
                    .background(FrostedGlassView()) // Use Frosted Glass for the text field
                    .cornerRadius(20)

                Button(action: sendMessage) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.system(size: 36))
                        .foregroundStyle(Color.neuraPrimaryGradient) // Use gradient
                }
                .disabled(messageText.isEmpty)
            }
            .padding()
        }
        .background(Color.neuraBackground.ignoresSafeArea())
    }
    
    func sendMessage() {
        let trimmedMessage = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedMessage.isEmpty else { return }
        
        messageText = "" // Clear the text field immediately
        
        Task {
            await viewModel.sendMessage(trimmedMessage)
        }
    }
}

// A sub-view for a single chat bubble
struct MessageView: View {
    let message: ChatMessage
    
    var body: some View {
        HStack {
            if message.author == .user {
                Spacer(minLength: 50)
            }
            
            if message.isLoading {
                // "Thinking" indicator with a cool animation
                HStack(spacing: 5) {
                    DotView(delay: 0)
                    DotView(delay: 0.2)
                    DotView(delay: 0.4)
                }
                .padding()
                .background(Color.neuraSurface)
                .cornerRadius(20, corners: [.topLeft, .topRight, .bottomLeft])
                
            } else {
                Text(message.text)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                    .foregroundColor(.white)
                    .background(message.author == .user ? AnyShapeStyle(Color.neuraPrimaryGradient) : AnyShapeStyle(Color.neuraSurface))
                    .cornerRadius(20, corners: message.author == .user ? [.topLeft, .topRight, .bottomLeft] : [.topLeft, .topRight, .bottomRight])
            }

            if message.author == .agent {
                Spacer(minLength: 50)
            }
        }
        .padding(.horizontal)
    }
}

// Helper to selectively round corners of a view
extension View {
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCorner(radius: radius, corners: corners))
    }
}

struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners
    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(roundedRect: rect, byRoundingCorners: corners, cornerRadii: CGSize(width: radius, height: radius))
        return Path(path.cgPath)
    }
}

// A simple dot for the "thinking" animation
struct DotView: View {
    @State private var scale: CGFloat = 0.5
    let delay: Double

    var body: some View {
        Circle()
            .frame(width: 8, height: 8)
            .scaleEffect(scale)
            .onAppear {
                withAnimation(Animation.easeInOut(duration: 0.6).repeatForever().delay(delay)) {
                    self.scale = 1
                }
            }
    }
}

