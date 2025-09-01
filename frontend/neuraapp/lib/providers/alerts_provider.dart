import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/alert_model.dart';
import '../utils/constants.dart';
import 'services_provider.dart';

// A StreamProvider is used to listen to a stream (like a WebSocket) and expose
// its values to the UI.
final alertsProvider = StreamProvider.autoDispose<Alert>((ref) async* {
  final storage = ref.watch(secureStorageProvider);
  final token = await storage.getToken();

  if (token == null) {
    // If there's no token, we can't connect.
    throw Exception('Authentication token not found.');
  }

  final uri = Uri.parse('${AppConstants.alertsWebSocketUrl}?token=$token');
  final channel = WebSocketChannel.connect(uri);

  // When the provider is destroyed, close the connection to prevent memory leaks.
  ref.onDispose(() => channel.sink.close());

  // Listen to the stream of messages from the WebSocket.
  // The 'await for' loop continues as long as the stream is open.
  await for (final message in channel.stream) {
    // Each message is a JSON string. We decode it and convert it to an Alert object.
    final data = jsonDecode(message);
    // 'yield' is like 'return', but for streams. It emits a value without
    // terminating the function.
    yield Alert.fromJson(data);
  }
});