//
//  WebSocketService.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import Foundation
import Combine

@MainActor
class WebSocketService: NSObject, ObservableObject, URLSessionWebSocketDelegate {
    
    // We will publish received alerts to any part of the app that is listening.
    @Published var latestAlert: Alert?

    private var webSocketTask: URLSessionWebSocketTask?
    private let keychainService = KeychainService.shared
    
    func connect() {
        guard let token = keychainService.getToken(),
              let url = URL(string: "\(Constants.alertsWebSocketUrl)?token=\(token)") else {
            print("WebSocket Error: Cannot connect. Missing token or invalid URL.")
            return
        }
        
        let request = URLRequest(url: url)
        webSocketTask = URLSession(configuration: .default, delegate: self, delegateQueue: OperationQueue()).webSocketTask(with: request)
        webSocketTask?.resume()
        
        receiveMessage()
    }
    
    func disconnect() {
        webSocketTask?.cancel(with: .goingAway, reason: nil)
    }
    
    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .failure(let error):
                print("WebSocket Error: Failed to receive message: \(error.localizedDescription)")
            case .success(let message):
                switch message {
                case .string(let text):
                    print("WebSocket: Received text message.")
                    self?.decode(text)
                case .data(let data):
                    print("WebSocket: Received binary data.")
                    // Handle binary data if needed
                @unknown default:
                    fatalError()
                }
                
                // Continue listening for the next message
                self?.receiveMessage()
            }
        }
    }
    
    private func decode(_ jsonString: String) {
        guard let data = jsonString.data(using: .utf8) else {
            print("WebSocket Decode Error: Could not convert string to data.")
            return
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        do {
            let alert = try decoder.decode(Alert.self, from: data)
            // Update the published property on the main thread
            DispatchQueue.main.async {
                self.latestAlert = alert
            }
        } catch {
            print("WebSocket Decode Error: \(error.localizedDescription)")
            print("Original JSON: \(jsonString)")
        }
    }
    
    // Delegate methods for monitoring connection status
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didOpenWithProtocol protocol: String?) {
        print("WebSocket: Connection opened")
    }
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        print("WebSocket: Connection closed")
    }
}
