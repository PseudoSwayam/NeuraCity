import Foundation
import Combine

@MainActor
class WebSocketService: NSObject, ObservableObject, URLSessionWebSocketDelegate {
    
    @Published var latestAlert: Alert?

    private var webSocketTask: URLSessionWebSocketTask?
    private let keychainService = KeychainService.shared
    
    private let jsonDecoder: JSONDecoder = {
        let decoder = JSONDecoder()
        
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
        formatter.calendar = Calendar(identifier: .iso8601)
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.locale = Locale(identifier: "en_US_POSIX")

        decoder.dateDecodingStrategy = .formatted(formatter)
        
        return decoder
    }()

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
                    Task { [weak self] in
                        await self?.decode(text)
                    }
                case .data:
                    print("WebSocket: Received unexpected binary data.")
                @unknown default:
                    fatalError()
                }
                
                self?.receiveMessage()
            }
        }
    }
    
    private func decode(_ jsonString: String) async {
        guard let data = jsonString.data(using: .utf8) else {
            print("WebSocket Decode Error: Could not convert string to data.")
            return
        }
        
        do {
            let alert = try self.jsonDecoder.decode(Alert.self, from: data)
            self.latestAlert = alert
        } catch {
            print("WebSocket Decode Error: \(error.localizedDescription)")
            if let decodingError = error as? DecodingError {
                print("Decoding Error Details: \(decodingError)")
            }
            print("Original JSON: \(jsonString)")
        }
    }
    
    // Delegate methods...
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didOpenWithProtocol protocol: String?) {
        print("WebSocket: Connection opened")
    }
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        print("WebSocket: Connection closed")
    }
}
