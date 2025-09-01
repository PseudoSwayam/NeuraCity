import 'package:firebase_messaging/firebase_messaging.dart';

class NotificationService {
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;

  Future<void> initialize() async {
    // This will handle messages that are received when the app is terminated.
    FirebaseMessaging.instance.getInitialMessage();

    // This will handle messages received while the app is in the foreground.
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Got a message whilst in the foreground!');
      print('Message data: ${message.data}');
      if (message.notification != null) {
        print('Message also contained a notification: ${message.notification}');
      }
    });
  }

  // Request permission from the user to receive push notifications.
  Future<bool> requestPermission() async {
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );

    return settings.authorizationStatus == AuthorizationStatus.authorized;
  }

  // Get the unique FCM device token.
  Future<String?> getFCMToken() async {
    // You must request permission before getting the token on iOS.
    return await _firebaseMessaging.getToken();
  }
}