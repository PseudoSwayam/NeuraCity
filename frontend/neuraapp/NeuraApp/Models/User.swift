//
//  User.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import Foundation

// A struct is a simple value type in Swift.
// 'Codable' is a powerful protocol that lets us easily convert this struct from/to JSON.
struct User: Codable, Identifiable {
    let id: Int
    let email: String
    let fullName: String
    let role: String
    let isActive: Bool

    // This tells the decoder how to map JSON keys (like "full_name") to our Swift properties.
    enum CodingKeys: String, CodingKey {
        case id, email, role
        case fullName = "full_name"
        case isActive = "is_active"
    }
}
