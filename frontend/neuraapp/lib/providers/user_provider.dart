import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_model.dart'; 
import 'services_provider.dart';

final userProvider = FutureProvider.autoDispose<User>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getMyProfile();
});