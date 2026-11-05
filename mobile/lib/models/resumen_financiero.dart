class HistorialDeuda {
  const HistorialDeuda({
    required this.idFactura,
    required this.mes,
    required this.mesNombre,
    required this.anio,
    required this.fechaVencimiento,
    required this.estado,
    required this.estadoNombre,
    required this.total,
    required this.totalPagado,
    required this.saldo,
  });

  final int idFactura;
  final int mes;
  final String mesNombre;
  final int anio;
  final String fechaVencimiento;
  final String estado;
  final String estadoNombre;
  final String total;
  final String totalPagado;
  final String saldo;

  factory HistorialDeuda.fromJson(Map<String, dynamic> json) {
    return HistorialDeuda(
      idFactura: json['id_factura'] as int,
      mes: json['mes'] as int,
      mesNombre: json['mes_nombre'].toString(),
      anio: json['anio'] as int,
      fechaVencimiento: json['fecha_vencimiento'].toString(),
      estado: json['estado'].toString(),
      estadoNombre: json['estado_nombre'].toString(),
      total: json['total'].toString(),
      totalPagado: json['total_pagado'].toString(),
      saldo: json['saldo'].toString(),
    );
  }
}

class ResumenFinanciero {
  const ResumenFinanciero({
    required this.totalFacturado,
    required this.totalPagado,
    required this.deudaActual,
    required this.cantidadFacturas,
    required this.pendientes,
    required this.parciales,
    required this.pagadas,
    required this.vencidas,
    required this.anuladas,
    required this.historialDeuda,
  });

  final String totalFacturado;
  final String totalPagado;
  final String deudaActual;

  final int cantidadFacturas;
  final int pendientes;
  final int parciales;
  final int pagadas;
  final int vencidas;
  final int anuladas;

  final List<HistorialDeuda> historialDeuda;

  factory ResumenFinanciero.fromJson(Map<String, dynamic> json) {
    final resumen = json['resumen'] as Map<String, dynamic>;

    final historialJson = json['historial_deuda'] as List<dynamic>? ?? [];

    return ResumenFinanciero(
      totalFacturado: resumen['total_facturado'].toString(),
      totalPagado: resumen['total_pagado'].toString(),
      deudaActual: resumen['deuda_actual'].toString(),
      cantidadFacturas: resumen['cantidad_facturas'] as int,
      pendientes: resumen['pendientes'] as int,
      parciales: resumen['parciales'] as int,
      pagadas: resumen['pagadas'] as int,
      vencidas: resumen['vencidas'] as int,
      anuladas: resumen['anuladas'] as int,
      historialDeuda: historialJson
          .map((item) => HistorialDeuda.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}
