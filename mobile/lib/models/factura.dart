class DetalleFactura {
  const DetalleFactura({
    required this.idDetalle,
    required this.tipoConcepto,
    required this.descripcion,
    required this.importe,
    required this.totalPagado,
    required this.saldoPendiente,
    required this.saldoDisponiblePago,
  });

  final int idDetalle;
  final String tipoConcepto;
  final String descripcion;
  final String importe;
  final String totalPagado;
  final String saldoPendiente;
  final String saldoDisponiblePago;

  factory DetalleFactura.fromJson(Map<String, dynamic> json) {
    return DetalleFactura(
      idDetalle: json['id_detalle'] as int,
      tipoConcepto: json['tipo_concepto'] as String,
      descripcion: json['descripcion'] as String,
      importe: json['importe'].toString(),
      totalPagado: json['total_pagado'].toString(),
      saldoPendiente: json['saldo_pendiente'].toString(),
      saldoDisponiblePago: json['saldo_disponible_pago']?.toString() ?? '0.00',
    );
  }
}

class Factura {
  const Factura({
    required this.idFactura,
    required this.mes,
    required this.mesNombre,
    required this.anio,
    required this.fechaEmision,
    required this.fechaVencimiento,
    required this.estado,
    required this.estadoNombre,
    required this.total,
    required this.totalPagado,
    required this.saldo,
    required this.detalles,
  });

  final int idFactura;
  final int mes;
  final String mesNombre;
  final int anio;
  final String fechaEmision;
  final String fechaVencimiento;
  final String estado;
  final String estadoNombre;
  final String total;
  final String totalPagado;
  final String saldo;
  final List<DetalleFactura> detalles;

  factory Factura.fromJson(Map<String, dynamic> json) {
    final detallesJson = json['detalles'] as List<dynamic>? ?? [];

    return Factura(
      idFactura: json['id_factura'] as int,
      mes: json['mes'] as int,
      mesNombre: json['mes_nombre'] as String,
      anio: json['anio'] as int,
      fechaEmision: json['fecha_emision'].toString(),
      fechaVencimiento: json['fecha_vencimiento'].toString(),
      estado: json['estado'] as String,
      estadoNombre: json['estado_nombre'] as String,
      total: json['total'].toString(),
      totalPagado: json['total_pagado'].toString(),
      saldo: json['saldo'].toString(),
      detalles: detallesJson
          .map((item) => DetalleFactura.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}
