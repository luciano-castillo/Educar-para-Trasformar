import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/api_config.dart';

class SessionService {
  static String get _tokenKey {
    return 'auth_token_${ApiConfig.environment}';
  }

  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  Future<void> guardarToken(String token) async {
    await _storage.write(key: _tokenKey, value: token);
  }

  Future<String?> obtenerToken() async {
    return _storage.read(key: _tokenKey);
  }

  Future<void> eliminarToken() async {
    await _storage.delete(key: _tokenKey);
  }
}
