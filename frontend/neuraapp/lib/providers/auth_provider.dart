import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:neuraapp/providers/services_provider.dart';
import 'package:neuraapp/services/api_service.dart';

class AuthState {
  final bool isAuthenticated;
  final bool isLoading;
  final String? error;

  AuthState({this.isAuthenticated = false, this.isLoading = false, this.error});

  AuthState copyWith({bool? isAuthenticated, bool? isLoading, String? error}) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final Ref _ref;
  AuthNotifier(this._ref) : super(AuthState());

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final apiService = _ref.read(apiServiceProvider);
      final token = await apiService.login(email, password);
      await _ref.read(secureStorageProvider).saveToken(token);

      final user = await apiService.getMyProfile();
      await apiService.performCheckIn(user.id);

      // This will now call the existing method and work correctly.
      await _handlePushNotificationRegistration();
      state = state.copyWith(isLoading: false, isAuthenticated: true);

    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString().replaceFirst("Exception: ", ""));
    }
  }
  
  Future<void> _handlePushNotificationRegistration() async {
    final notificationService = _ref.read(notificationServiceProvider);
    final ApiService apiService = _ref.read(apiServiceProvider);
    
    final permissionGranted = await notificationService.requestPermission();
    if (permissionGranted) {
      final fcmToken = await notificationService.getFCMToken();
      if (fcmToken != null) {
        await apiService.registerDevice(fcmToken);
      }
    }
  }

  Future<void> logout() async {
    await _ref.read(secureStorageProvider).deleteToken();
    state = AuthState();
  }

  Future<void> checkAuthStatus() async {
    state = state.copyWith(isLoading: true);
    final token = await _ref.read(secureStorageProvider).getToken();
    state = state.copyWith(
      isLoading: false, 
      isAuthenticated: token != null && token.isNotEmpty
    );
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref);
});