//
//  Color+Extensions.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import SwiftUI

extension Color {
    // Existing Palette
    static let neuraBackground = Color(red: 18/255, green: 18/255, blue: 18/255)
    static let neuraSurface = Color(red: 30/255, green: 30/255, blue: 30/255)
    static let neuraPrimary = Color(red: 66/255, green: 165/255, blue: 245/255)
    static let neuraAccent = Color(red: 0/255, green: 230/255, blue: 118/255)

    // New LinearGradient for our primary buttons for an eye-catchy effect.
    static let neuraPrimaryGradient = LinearGradient(
        gradient: Gradient(colors: [Color.neuraPrimary, Color(red: 25/255, green: 118/255, blue: 210/255)]),
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
}
