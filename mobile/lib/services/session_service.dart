import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SessionService {
  static const _tokenKey = 'auth_token';

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
