import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../models/resumen_financiero.dart';

class ResumenFinancieroService {
  Future<ResumenFinanciero> obtenerResumen({
    required String token,
    required int idAlumno,
  }) async {
    final response = await http.get(
      Uri.parse(
        '${ApiConfig.baseUrl}/mis-hijos/'
        '$idAlumno/resumen-financiero/',
      ),
      headers: {'Authorization': 'Token $token'},
    );

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode != 200) {
      throw Exception(
        data['detail'] ?? 'No se pudo obtener el resumen financiero.',
      );
    }

    return ResumenFinanciero.fromJson(data);
  }
}
