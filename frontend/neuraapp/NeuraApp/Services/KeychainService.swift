//
//  KeychainService.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 01/09/25.
//

import Foundation
import Security

// A class for managing secure data storage.
class KeychainService {
    // A shared instance (Singleton pattern) so the whole app uses the same service.
    static let shared = KeychainService()
    
    // Private init to enforce the singleton pattern.
    private init() {}
    
    // Generic function to save data to the keychain.
    func save(key: String, data: Data) {
        let query = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrAccount: key,
            kSecValueData: data
        ] as [String: Any]
        
        // Delete any old item with the same key.
        SecItemDelete(query as CFDictionary)
        
        // Add the new item.
        SecItemAdd(query as CFDictionary, nil)
    }

    // Generic function to load data from the keychain.
    func load(key: String) -> Data? {
        let query = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrAccount: key,
            kSecReturnData: kCFBooleanTrue!,
            kSecMatchLimit: kSecMatchLimitOne
        ] as [String: Any]

        var dataTypeRef: AnyObject? = nil
        let status: OSStatus = SecItemCopyMatching(query as CFDictionary, &dataTypeRef)
        
        if status == noErr {
            return dataTypeRef as! Data?
        } else {
            return nil
        }
    }

    // A convenience method specifically for our JWT token.
    func saveToken(_ token: String) {
        guard let data = token.data(using: .utf8) else { return }
        save(key: "jwt_token", data: data)
    }

    func getToken() -> String? {
        guard let data = load(key: "jwt_token") else { return nil }
        return String(data: data, encoding: .utf8)
    }
    
    func deleteToken() {
        let query = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrAccount: "jwt_token"
        ] as [String: Any]
        SecItemDelete(query as CFDictionary)
    }
}
