//
//  NotificationService.swift
//  NeuraApp
//
//  Created by Swayam  Sahoo on 03/09/25.
//

import Foundation
import UserNotifications

class NotificationService {
    static let shared = NotificationService()
    
    // 1. Request Permission from the user
    func requestPermission() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                print("Notification permission granted.")
            } else if let error = error {
                print("Notification permission error: \(error.localizedDescription)")
            }
        }
    }
    
    // 2. Schedule and show a local notification based on a received alert
    func scheduleNotification(for alert: Alert) {
        let content = UNMutableNotificationContent()
        content.title = alert.location // e.g., "Fire Cam"
        content.body = alert.humanReadableMessage // The full alert text
        content.sound = .default
        
        // Trigger the notification to show in 1 second
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 1, repeats: false)
        
        // Create the request
        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: trigger)
        
        // Add the request to the notification center
        UNUserNotificationCenter.current().add(request)
    }
}
