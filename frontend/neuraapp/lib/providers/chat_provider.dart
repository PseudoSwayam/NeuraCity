import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/chat_message_model.dart';
import 'services_provider.dart';

// The state for this provider is the list of chat messages itself.
class ChatNotifier extends StateNotifier<List<ChatMessage>> {
  final Ref _ref;
  ChatNotifier(this._ref) : super([]); // Initial state is an empty list.

  Future<void> sendMessage(String text) async {
    // 1. Immediately add the user's message to the chat list for a responsive feel.
    state = [
      ...state,
      ChatMessage(text: text, author: MessageAuthor.user)
    ];
    
    // 2. Add a loading indicator to show the AI is "thinking".
    final loadingMessage = ChatMessage(text: "...", author: MessageAuthor.agent, isLoading: true);
    state = [...state, loadingMessage];
    
    try {
      final apiService = _ref.read(apiServiceProvider);
      // 3. Call the API.
      final response = await apiService.submitQuery(text);
      final agentMessage = ChatMessage(text: response, author: MessageAuthor.agent);
      
      // 4. Replace the loading message with the actual response.
      state = [
        for (final message in state)
          if (message == loadingMessage) agentMessage else message
      ];
    } catch (e) {
      final errorMessage = ChatMessage(text: "Sorry, I encountered an error.", author: MessageAuthor.agent);
       // 5. If there's an error, replace the loading message with an error message.
       state = [
        for (final message in state)
          if (message == loadingMessage) errorMessage else message
      ];
    }
  }
}

final chatProvider = StateNotifierProvider.autoDispose<ChatNotifier, List<ChatMessage>>((ref) {
  return ChatNotifier(ref);
});