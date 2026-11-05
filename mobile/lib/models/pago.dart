class DetallePago {
  const DetallePago({
    required this.idPagoDetalle,
    required this.concepto,
    required this.importeAplicado,
  });

  final int idPagoDetalle;
  final String concepto;
  final String importeAplicado;

  factory DetallePago.fromJson(Map<String, dynamic> json) {
    return DetallePago(
      idPagoDetalle: json['id_pago_detalle'] as int,
      concepto: json['concepto']?.toString() ?? '',
      importeAplicado: json['importe_aplicado']?.toString() ?? '0.00',
    );
  }
}

class ComprobantePago {
  const ComprobantePago({
    required this.idComprobante,
    required this.archivoUrl,
    required this.fechaSubida,
  });

  final int idComprobante;
  final String archivoUrl;
  final String fechaSubida;

  factory ComprobantePago.fromJson(Map<String, dynamic> json) {
    return ComprobantePago(
      idComprobante: json['id_comprobante'] as int,
      archivoUrl: json['archivo_url']?.toString() ?? '',
      fechaSubida: json['fecha_subida']?.toString() ?? '',
    );
  }
}

class Pago {
  const Pago({
    required this.idPago,
    required this.idFactura,
    required this.mes,
    required this.mesNombre,
    required this.anio,
    required this.fechaTransferencia,
    required this.monto,
    required this.numeroOperacion,
    required this.estado,
    required this.estadoNombre,
    required this.observaciones,
    required this.fechaRegistro,
    required this.detalles,
    required this.comprobantes,
  });

  final int idPago;
  final int idFactura;
  final int mes;
  final String mesNombre;
  final int anio;

  final String fechaTransferencia;
  final String monto;
  final String numeroOperacion;
  final String estado;
  final String estadoNombre;
  final String observaciones;
  final String fechaRegistro;

  final List<DetallePago> detalles;
  final List<ComprobantePago> comprobantes;

  factory Pago.fromJson(Map<String, dynamic> json) {
    final detallesJson = json['detalles_pago'] as List<dynamic>? ?? [];

    final comprobantesJson = json['comprobantes'] as List<dynamic>? ?? [];

    return Pago(
      idPago: json['id_pago'] as int,
      idFactura: json['id_factura'] as int,
      mes: json['mes'] as int,
      mesNombre: json['mes_nombre']?.toString() ?? '',
      anio: json['anio'] as int,
      fechaTransferencia: json['fecha_transferencia']?.toString() ?? '',
      monto: json['monto']?.toString() ?? '0.00',
      numeroOperacion: json['numero_operacion']?.toString() ?? '',
      estado: json['estado']?.toString() ?? '',
      estadoNombre: json['estado_nombre']?.toString() ?? '',
      observaciones: json['observaciones']?.toString() ?? '',
      fechaRegistro: json['fecha_registro']?.toString() ?? '',
      detalles: detallesJson
          .map((item) => DetallePago.fromJson(item as Map<String, dynamic>))
          .toList(),
      comprobantes: comprobantesJson
          .map((item) => ComprobantePago.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}
