//
//  Constants.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import Foundation

// Using an enum without cases is a common Swift pattern for namespacing constants.
enum Constants {
    // IMPORTANT: Use "localhost" (127.0.0.1) for testing on the iOS Simulator.
    // If you ever test on a real iPhone, you'll need to change this to your Mac's IP.
    static let serverIP = "127.0.0.1"

    static let userHubBaseUrl = "http://\(serverIP):8005"
    static let nlpAgentBaseUrl = "http://\(serverIP):8000"
    static let alertsWebSocketUrl = "ws://\(serverIP):8003/ws/alerts"
}
