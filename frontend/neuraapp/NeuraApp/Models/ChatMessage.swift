//
//  ChatMessage.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import Foundation

// A unique ID is needed for lists in SwiftUI to perform well.
struct ChatMessage: Identifiable {
    let id = UUID()
    let text: String
    let author: MessageAuthor
    var isLoading: Bool = false
}

enum MessageAuthor {
    case user
    case agent
}
