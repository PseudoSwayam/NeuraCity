class User {
  final int id;
  final String email;
  final String fullName;
  final String role;
  final bool isActive;

  User({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
    required this.isActive,
  });

  // CHANGED: This factory now parses all the fields from the /users/me endpoint.
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? 0,
      email: json['email'] ?? 'No email provided',
      fullName: json['full_name'] ?? 'Guest User',
      role: json['role'] ?? 'user',
      isActive: json['is_active'] ?? false,
    );
  }
}