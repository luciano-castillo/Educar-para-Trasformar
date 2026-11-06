import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';

import '../config/api_config.dart';
import '../models/pago.dart';

class PagosService {
  Future<List<Pago>> obtenerPagos({
    required String token,
    required int idAlumno,
    required int idFactura,
  }) async {
    final response = await http.get(
      Uri.parse(
        '${ApiConfig.baseUrl}/mis-hijos/'
        '$idAlumno/facturas/$idFactura/pagos/',
      ),
      headers: {'Authorization': 'Token $token'},
    );

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode != 200) {
      throw Exception(data['detail'] ?? 'No se pudieron obtener los pagos.');
    }

    final pagosJson = data['pagos'] as List<dynamic>? ?? [];

    return pagosJson
        .map((item) => Pago.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<Pago>> obtenerHistorialPagos({
    required String token,
    required int idAlumno,
  }) async {
    final response = await http.get(
      Uri.parse(
        '${ApiConfig.baseUrl}/mis-hijos/'
        '$idAlumno/historial-pagos/',
      ),
      headers: {'Authorization': 'Token $token'},
    );

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode != 200) {
      throw Exception(
        data['detail'] ??
            'No se pudo obtener '
                'el historial de pagos.',
      );
    }

    final pagosJson = data['pagos'] as List<dynamic>? ?? [];

    return pagosJson
        .map((item) => Pago.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<String> registrarPago({
    required String token,
    required int idAlumno,
    required int idFactura,
    required DateTime fechaTransferencia,
    required List<Map<String, dynamic>> aplicaciones,
    required List<PlatformFile> comprobantes,
    String numeroOperacion = '',
    String observaciones = '',
  }) async {
    final fecha =
        '${fechaTransferencia.year.toString().padLeft(4, '0')}-'
        '${fechaTransferencia.month.toString().padLeft(2, '0')}-'
        '${fechaTransferencia.day.toString().padLeft(2, '0')}';

    final request = http.MultipartRequest(
      'POST',
      Uri.parse(
        '${ApiConfig.baseUrl}/mis-hijos/'
        '$idAlumno/facturas/$idFactura/'
        'registrar-pago/',
      ),
    );

    request.headers['Authorization'] = 'Token $token';

    request.fields['fecha_transferencia'] = fecha;

    request.fields['aplicaciones'] = jsonEncode(aplicaciones);

    request.fields['numero_operacion'] = numeroOperacion;

    request.fields['observaciones'] = observaciones;

    for (final archivo in comprobantes) {
      final bytes = await archivo.readAsBytes();

      request.files.add(
        http.MultipartFile.fromBytes(
          'comprobantes',
          bytes,
          filename: archivo.name,
        ),
      );
    }

    final streamedResponse = await request.send();

    final response = await http.Response.fromStream(streamedResponse);

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode == 201) {
      return data['mensaje']?.toString() ?? 'Pago registrado correctamente.';
    }

    throw Exception(data['detail'] ?? 'No se pudo registrar el pago.');
  }

  Future<String> descargarComprobante({
  required String token,
  required int idAlumno,
  required int idComprobante,
  }) async {
    final response = await http.get(
      Uri.parse(
        '${ApiConfig.baseUrl}/mis-hijos/'
        '$idAlumno/comprobantes/'
        '$idComprobante/archivo/',
      ),
      headers: {
        'Authorization': 'Token $token',
      },
    );

    if (response.statusCode != 200) {
      throw Exception(
        'No se pudo descargar el comprobante.',
      );
    }

    final contentDisposition =
        response.headers['content-disposition'] ?? '';

    final match = RegExp(
      r'filename="?([^";]+)"?',
    ).firstMatch(contentDisposition);

    var nombreArchivo =
        match?.group(1) ??
        'comprobante_$idComprobante';

    nombreArchivo = nombreArchivo.replaceAll(
      RegExp(r'[\\/]'),
      '_',
    );

    final archivo = File(
      '${Directory.systemTemp.path}/'
      '$nombreArchivo',
    );

    await archivo.writeAsBytes(
      response.bodyBytes,
      flush: true,
    );

    return archivo.path;
  }
}
