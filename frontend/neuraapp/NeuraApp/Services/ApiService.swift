import Foundation

// Custom Errors remain the same.
enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case requestFailed(description: String)
    case decodingError

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "The server URL is invalid."
        case .invalidResponse: return "The server returned an invalid response."
        case .requestFailed(let description): return description
        case .decodingError: return "There was an error decoding the server's response."
        }
    }
}

class ApiService {
    static let shared = ApiService()
    private let keychainService = KeychainService.shared

    private let jsonDecoder: JSONDecoder = {
        let decoder = JSONDecoder()
        
        // 1. Create a Date Formatter that understands fractional seconds.
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS" // This MUST match your backend's format
        formatter.calendar = Calendar(identifier: .iso8601)
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.locale = Locale(identifier: "en_US_POSIX")

        // 2. Tell the decoder to use our custom formatter.
        decoder.dateDecodingStrategy = .formatted(formatter)
        
        return decoder
    }()
    
    // MARK: - Module 1: UserHub

    func login(email: String, password: String) async throws -> String {
        guard let url = URL(string: "\(Constants.userHubBaseUrl)/auth/token") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        var components = URLComponents()
        components.queryItems = [
            URLQueryItem(name: "username", value: email),
            URLQueryItem(name: "password", value: password)
        ]
        request.httpBody = components.query?.data(using: .utf8)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw APIError.requestFailed(description: "Invalid email or password.")
        }
        
        do {
            let loginResponse = try jsonDecoder.decode(LoginResponse.self, from: data)
            return loginResponse.accessToken
        } catch {
            throw APIError.decodingError
        }
    }

    func getMyProfile() async throws -> User {
        guard let url = URL(string: "\(Constants.userHubBaseUrl)/users/me") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        guard let token = keychainService.getToken() else {
            throw APIError.requestFailed(description: "User is not authenticated.")
        }
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        do {
            let user = try jsonDecoder.decode(User.self, from: data)
            return user
        } catch {
            throw APIError.decodingError
        }
    }

    func performCheckIn(forUser user: User) async throws {
        guard let url = URL(string: "\(Constants.userHubBaseUrl)/attendance/check-in") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        guard let token = keychainService.getToken() else {
            throw APIError.requestFailed(description: "User is not authenticated.")
        }
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["user_id": user.id, "location": "NeuraApp Mobile Login"] as [String: Any]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode != 200 {
            print("Check-in failed with status code: \(httpResponse.statusCode)")
        }
    }

    // MARK: - Module 2: NeuraNLP Agent
    
    func submitQuery(_ query: String) async throws -> String {
        guard let url = URL(string: "\(Constants.nlpAgentBaseUrl)/query") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        guard let token = keychainService.getToken() else {
            throw APIError.requestFailed(description: "User is not authenticated.")
        }
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"query\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(query)\r\n".data(using: .utf8)!)
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"mode\"\r\n\r\n".data(using: .utf8)!)
        body.append("text\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        struct NLPResponse: Codable { let response: String }

        do {
            let nlpResponse = try jsonDecoder.decode(NLPResponse.self, from: data)
            return nlpResponse.response
        } catch {
            throw APIError.decodingError
        }
    }
}
