import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../models/factura.dart';

class FacturasService {
  Future<List<Factura>> obtenerFacturas({
    required String token,
    required int idAlumno,
  }) async {
    final response = await http.get(
      Uri.parse(
        '${ApiConfig.baseUrl}/'
        'mis-hijos/$idAlumno/facturas/',
      ),
      headers: {'Authorization': 'Token $token'},
    );

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode != 200) {
      throw Exception(data['detail'] ?? 'No se pudieron obtener las facturas.');
    }

    final facturasJson = data['facturas'] as List<dynamic>;

    return facturasJson
        .map((item) => Factura.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}
