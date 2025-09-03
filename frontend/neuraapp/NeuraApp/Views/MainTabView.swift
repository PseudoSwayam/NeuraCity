//
//  MainTabView.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import SwiftUI

struct MainTabView: View {
    // This creates and keeps our WebSocketService alive for the whole session.
    @StateObject private var webSocketService = WebSocketService()
    
    var body: some View {
        TabView {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
            
            ChatView()
                .tabItem {
                    Label("Chat AI", systemImage: "message.fill")
                }
            
            MapView()
                .tabItem {
                    Label("Map", systemImage: "map.fill")
                }
        }
        // This makes our Tab Bar have the correct dark styling
        .onAppear {
            let appearance = UITabBarAppearance()
            appearance.backgroundColor = UIColor(Color.neuraSurface)
            UITabBar.appearance().standardAppearance = appearance
            UITabBar.appearance().scrollEdgeAppearance = appearance
            
            // Connect to the websocket as soon as the user logs in
            webSocketService.connect()
        }
        // We pass the websocket service down to all child views so they can use it.
        .environmentObject(webSocketService)
    }
}

