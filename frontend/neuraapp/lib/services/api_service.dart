import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:neuraapp/models/user_model.dart';
import '../utils/constants.dart';
import 'secure_storage_service.dart';

class ApiService {
  final SecureStorageService _storageService;

  ApiService(this._storageService);

  // Helper method for headers requiring authorization
  Future<Map<String, String>> _getAuthHeaders() async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('User not authenticated.');
    return {
      'Authorization': 'Bearer $token',
    };
  }

  // Endpoint 1.1: User Login
  Future<String> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('${AppConstants.userHubBaseUrl}/auth/token'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {'username': email, 'password': password},
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body)['access_token'];
    } else {
      throw Exception('Invalid email or password.');
    }
  }

  // Endpoint 1.2: Get My Profile
  Future<User> getMyProfile() async {
    final headers = await _getAuthHeaders();
    final response = await http.get(
      Uri.parse('${AppConstants.userHubBaseUrl}/users/me'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      return User.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load user profile. Your session may have expired.');
    }
  }

  // Endpoint 2.1: Submit a Query
  Future<String> submitQuery(String query) async {
    final headers = await _getAuthHeaders();
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('${AppConstants.nlpAgentBaseUrl}/query'),
    );
    request.headers.addAll(headers);
    request.fields['query'] = query;
    request.fields['mode'] = 'text';

    var streamedResponse = await request.send();
    var response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      return jsonDecode(response.body)['response'];
    } else {
      throw Exception('Failed to get response from AI agent.');
    }
  }

  // Endpoint 1.3: Check-In/Out
  Future<void> performCheckIn(int userId) async {
    final headers = await _getAuthHeaders();
    headers['Content-Type'] = 'application/json; charset=UTF-8';

    final body = jsonEncode({
      'user_id': userId,
      'location': 'NeuraApp Mobile Login',
    });

    try {
      await http.post(
        Uri.parse('${AppConstants.userHubBaseUrl}/attendance/check-in'),
        headers: headers,
        body: body,
      );
    } catch (e) {
      print("Check-in failed but not blocking user: $e");
    }
  }

  // THIS IS THE METHOD THAT WAS MISSING.
  // Purpose: Send the Firebase Cloud Messaging (FCM) token to the backend.
  Future<void> registerDevice(String fcmToken) async {
    try {
      final headers = await _getAuthHeaders();
      headers['Content-Type'] = 'application/json; charset=UTF-8';
      
      await http.post(
        // NOTE: This uses the future endpoint from the brief.
        Uri.parse('${AppConstants.userHubBaseUrl}/users/me/register-device'),
        headers: headers,
        body: jsonEncode(<String, String>{'fcm_token': fcmToken}),
      );
      print("FCM Token successfully registered with backend.");
    } catch (e) {
      print("Failed to register FCM token with backend: $e");
      // Not throwing an error as this is not a critical user-facing failure.
    }
  }
}