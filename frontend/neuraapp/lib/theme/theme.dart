import 'package:flutter/material.dart';

class AppTheme {
  static final ThemeData darkTheme = ThemeData(
    brightness: Brightness.dark,
    primaryColor: const Color(0xFF0D47A1), // A deep, modern blue
    scaffoldBackgroundColor: const Color(0xFF121212), // Standard dark background
    colorScheme: const ColorScheme.dark(
      primary: Color(0xFF42A5F5), // Brighter blue for interactive elements
      secondary: Color(0xFF00E676), // A vibrant accent green
      surface: Color(0xFF1E1E1E), // Card backgrounds
      onPrimary: Colors.white,
      onSecondary: Colors.black,
      onSurface: Colors.white,
      onError: Colors.black,
      error: Color(0xFFCF6679),
    ),
    cardColor: const Color(0xFF1E1E1E),
    textTheme: const TextTheme(
      displayLarge: TextStyle(fontSize: 96.0, fontWeight: FontWeight.w300, color: Colors.white),
      displayMedium: TextStyle(fontSize: 60.0, fontWeight: FontWeight.w400, color: Colors.white),
      displaySmall: TextStyle(fontSize: 48.0, fontWeight: FontWeight.w400, color: Colors.white),
      headlineMedium: TextStyle(fontSize: 34.0, fontWeight: FontWeight.w400, color: Colors.white),
      headlineSmall: TextStyle(fontSize: 24.0, fontWeight: FontWeight.w400, color: Colors.white),
      titleLarge: TextStyle(fontSize: 20.0, fontWeight: FontWeight.w500, color: Colors.white),
      bodyLarge: TextStyle(fontSize: 16.0, fontWeight: FontWeight.w400, color: Colors.white),
      bodyMedium: TextStyle(fontSize: 14.0, fontWeight: FontWeight.w400, color: Colors.white70),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.black.withOpacity(0.3),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8.0),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8.0),
        borderSide: const BorderSide(color: Color(0xFF42A5F5)),
      ),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Color(0xFF1E1E1E),
      selectedItemColor: Color(0xFF42A5F5),
      unselectedItemColor: Colors.grey,
    ),
  );
}