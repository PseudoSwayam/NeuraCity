//
//  ApiService.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import Foundation

// Define custom errors for better error handling in the UI.
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
        // This is crucial for correctly parsing the timestamps from your backend
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }()
    
    // MARK: - Module 1: UserHub

    /// Endpoint 1.1: User Login
    func login(email: String, password: String) async throws -> String {
        guard let url = URL(string: "\(Constants.userHubBaseUrl)/auth/token") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        // This sets the special header required by your backend
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        // This correctly formats the body as form data, not JSON
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

    /// Endpoint 1.2: Get My Profile
    func getMyProfile() async throws -> User {
        guard let url = URL(string: "\(Constants.userHubBaseUrl)/users/me") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        guard let token = keychainService.getToken() else {
            throw APIError.requestFailed(description: "User is not authenticated.")
        }
        // Set the Authorization header with our stored token
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

    /// Endpoint 1.3: Check-In
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
        
        // This is a "fire and forget" call, but we can check for a success code.
        let (_, response) = try await URLSession.shared.data(for: request)
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode != 200 {
            print("Check-in failed with status code: \(httpResponse.statusCode)")
        }
    }

    // MARK: - Module 2: NeuraNLP Agent

    /// Endpoint 2.1: Submit a Query
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

        // Creating a multipart/form-data body is more complex. We create a boundary to separate fields.
        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()
        
        // Add the 'query' text field
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"query\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(query)\r\n".data(using: .utf8)!)
        
        // Add the 'mode' text field
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"mode\"\r\n\r\n".data(using: .utf8)!)
        body.append("text\r\n".data(using: .utf8)!)
        
        // End the body with a closing boundary
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        // We need a specific struct to decode the response from the NLP agent
        struct NLPResponse: Codable {
            let response: String
        }

        do {
            let nlpResponse = try jsonDecoder.decode(NLPResponse.self, from: data)
            return nlpResponse.response
        } catch {
            print(String(data: data, encoding: .utf8) ?? "Could not print data")
            throw APIError.decodingError
        }
    }
}
