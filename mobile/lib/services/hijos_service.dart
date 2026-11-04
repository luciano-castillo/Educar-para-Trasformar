import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../models/hijo.dart';

class HijosService {
  Future<List<Hijo>> obtenerHijos({required String token}) async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/mis-hijos/'),
      headers: {'Authorization': 'Token $token'},
    );

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode != 200) {
      throw Exception(data['detail'] ?? 'No se pudieron obtener los hijos.');
    }

    final hijosJson = data['hijos'] as List<dynamic>;

    return hijosJson
        .map((item) => Hijo.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}
