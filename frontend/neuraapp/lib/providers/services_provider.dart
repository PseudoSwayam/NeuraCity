import 'package:flutter_riverpod/flutter_riverpod.dart';
// FIXED: Changed 'neurapp' to 'neuraapp'
import 'package:neuraapp/services/api_service.dart';
import 'package:neuraapp/services/notification_service.dart';
import 'package:neuraapp/services/secure_storage_service.dart';

final secureStorageProvider = Provider((ref) => SecureStorageService());

final apiServiceProvider = Provider((ref) {
  return ApiService(ref.watch(secureStorageProvider));
});

final notificationServiceProvider = Provider((ref) => NotificationService());