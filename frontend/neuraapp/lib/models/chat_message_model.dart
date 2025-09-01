// Differentiates who sent a message in the chat UI.
enum MessageAuthor { user, agent }

class ChatMessage {
  final String text;
  final MessageAuthor author;
  final bool isLoading; // Used to show the "thinking..." indicator

  ChatMessage({
    required this.text,
    required this.author,
    this.isLoading = false,
  });
}