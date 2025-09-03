//
//  FrostedGlassView.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 03/09/25.
//

import SwiftUI

// This is a special effect view that creates a translucent, blurred background.
struct FrostedGlassView: View {
    var body: some View {
        // ZStack allows us to layer views on top of each other.
        ZStack {
            // This is a special effect that adapts to light/dark mode.
            // It provides the blur and vibrancy.
            VisualEffectView(effect: UIBlurEffect(style: .systemThinMaterial))
            
            // We add a subtle white layer on top to "frost" the glass.
            Color.white.opacity(0.05)
        }
    }
}

// A helper struct to wrap UIKit's UIVisualEffectView for use in SwiftUI.
struct VisualEffectView: UIViewRepresentable {
    var effect: UIVisualEffect?
    func makeUIView(context: UIViewRepresentableContext<Self>) -> UIVisualEffectView { UIVisualEffectView() }
    func updateUIView(_ uiView: UIVisualEffectView, context: UIViewRepresentableContext<Self>) { uiView.effect = effect }
}
