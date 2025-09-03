import SwiftUI

struct AnimatedBlobBackground: View {
    @State private var animate = false

    var body: some View {
        ZStack {
            // The base dark background
            Color.neuraBackground.ignoresSafeArea()

            // A radial gradient for depth, similar to what we had before
            RadialGradient(gradient: Gradient(colors: [.neuraSurface.opacity(0.8), .neuraBackground]), center: .topLeading, startRadius: 5, endRadius: 900)
                .ignoresSafeArea()

            // The colorful, animated blobs
            ZStack {
                // Blob 1 (Blue)
                Circle()
                    .fill(Color.neuraPrimary)
                    .frame(width: 300, height: 300)
                    .offset(x: animate ? 100 : -100, y: animate ? -50 : -200)
                    .blur(radius: 120)

                // Blob 2 (Accent Green)
                Circle()
                    .fill(Color.neuraAccent)
                    .frame(width: 250, height: 250)
                    .offset(x: animate ? -100 : 100, y: animate ? 150 : 250)
                    .blur(radius: 100)
            }
        }
        .onAppear {
            // Start a slow, continuous, repeating animation when the view appears
            withAnimation(.easeInOut(duration: 20).repeatForever(autoreverses: true)) {
                animate.toggle()
            }
        }
    }
}
