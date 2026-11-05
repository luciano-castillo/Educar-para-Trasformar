import 'package:flutter/material.dart';

import 'historial_pagos_screen.dart';
import '../models/factura.dart';
import '../models/hijo.dart';
import '../models/resumen_financiero.dart';
import '../services/facturas_service.dart';
import '../services/resumen_financiero_service.dart';
import 'pagos_screen.dart';
import 'registrar_pago_screen.dart';

class FacturasScreen extends StatefulWidget {
  const FacturasScreen({super.key, required this.token, required this.hijo});

  final String token;
  final Hijo hijo;

  @override
  State<FacturasScreen> createState() {
    return _FacturasScreenState();
  }
}

class _FacturasScreenState extends State<FacturasScreen> {
  final _facturasService = FacturasService();

  final _resumenService = ResumenFinancieroService();

  late Future<List<Factura>> _facturasFuture;

  late Future<ResumenFinanciero> _resumenFuture;

  @override
  void initState() {
    super.initState();

    _cargarDatos();
  }

  void _cargarDatos() {
    _facturasFuture = _facturasService.obtenerFacturas(
      token: widget.token,
      idAlumno: widget.hijo.idAlumno,
    );

    _resumenFuture = _resumenService.obtenerResumen(
      token: widget.token,
      idAlumno: widget.hijo.idAlumno,
    );
  }

  Future<void> _recargar() async {
    setState(() {
      _cargarDatos();
    });

    await Future.wait([_facturasFuture, _resumenFuture]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Facturas')),
      body: RefreshIndicator(
        onRefresh: _recargar,
        child: FutureBuilder<List<Factura>>(
          future: _facturasFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }

            if (snapshot.hasError) {
              return ListView(
                children: [
                  const SizedBox(height: 120),
                  const Icon(Icons.error_outline, size: 64),
                  const SizedBox(height: 16),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 32),
                    child: Text(
                      snapshot.error.toString().replaceFirst('Exception: ', ''),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
              );
            }

            final facturas = snapshot.data ?? [];

            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text(
                  widget.hijo.nombreCompleto,
                  style: Theme.of(context).textTheme.titleLarge,
                ),

                const SizedBox(height: 4),

                Text('Legajo: ${widget.hijo.legajo}'),

                const SizedBox(height: 20),

                FutureBuilder<ResumenFinanciero>(
                  future: _resumenFuture,
                  builder: (context, resumenSnapshot) {
                    if (resumenSnapshot.connectionState ==
                        ConnectionState.waiting) {
                      return const Card(
                        child: Padding(
                          padding: EdgeInsets.all(24),
                          child: Center(child: CircularProgressIndicator()),
                        ),
                      );
                    }

                    if (resumenSnapshot.hasError) {
                      return Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Text(
                            resumenSnapshot.error.toString().replaceFirst(
                              'Exception: ',
                              '',
                            ),
                          ),
                        ),
                      );
                    }

                    final resumen = resumenSnapshot.data!;

                    return _ResumenFinancieroCard(
                      resumen: resumen,
                      token: widget.token,
                      hijo: widget.hijo,
                    );
                  },
                ),

                const SizedBox(height: 20),

                Text('Facturas', style: Theme.of(context).textTheme.titleLarge),

                const SizedBox(height: 12),

                if (facturas.isEmpty) ...[
                  const SizedBox(height: 40),
                  const Icon(Icons.receipt_long, size: 70),
                  const SizedBox(height: 16),
                  Text(
                    'No hay facturas para '
                    '${widget.hijo.nombreCompleto}.',
                    textAlign: TextAlign.center,
                  ),
                ],

                ...facturas.map(
                  (factura) => Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: _FacturaCard(
                      factura: factura,
                      token: widget.token,
                      hijo: widget.hijo,
                      onPagoRegistrado: _recargar,
                    ),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _ResumenFinancieroCard extends StatelessWidget {
  const _ResumenFinancieroCard({
    required this.resumen,
    required this.token,
    required this.hijo,
  });

  final ResumenFinanciero resumen;
  final String token;
  final Hijo hijo;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.account_balance_wallet_outlined),
                const SizedBox(width: 8),
                Text(
                  'Resumen financiero',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),

            const SizedBox(height: 16),

            _DatoResumen(
              titulo: 'Total facturado',
              valor: '\$${resumen.totalFacturado}',
            ),

            _DatoResumen(
              titulo: 'Total pagado',
              valor: '\$${resumen.totalPagado}',
            ),

            _DatoResumen(
              titulo: 'Deuda actual',
              valor: '\$${resumen.deudaActual}',
              destacado: true,
            ),

            const Divider(height: 28),

            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Chip(
                  label: Text(
                    'Pendientes: '
                    '${resumen.pendientes}',
                  ),
                ),
                Chip(
                  label: Text(
                    'Parciales: '
                    '${resumen.parciales}',
                  ),
                ),
                Chip(
                  label: Text(
                    'Pagadas: '
                    '${resumen.pagadas}',
                  ),
                ),
                Chip(
                  label: Text(
                    'Vencidas: '
                    '${resumen.vencidas}',
                  ),
                ),
              ],
            ),

            if (resumen.historialDeuda.isNotEmpty) ...[
              const Divider(height: 28),

              Text(
                'Historial de deuda',
                style: Theme.of(context).textTheme.titleSmall,
              ),

              const SizedBox(height: 8),

              ...resumen.historialDeuda.map(
                (deuda) => ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.warning_amber_outlined),
                  title: Text(
                    '${deuda.mesNombre} '
                    '${deuda.anio}',
                  ),
                  subtitle: Text(
                    '${deuda.estadoNombre} · '
                    'Vence: '
                    '${deuda.fechaVencimiento}',
                  ),
                  trailing: Text(
                    '\$${deuda.saldo}',
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                ),
              ),
            ],

            const SizedBox(height: 16),

            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) =>
                          HistorialPagosScreen(token: token, hijo: hijo),
                    ),
                  );
                },
                icon: const Icon(Icons.history),
                label: const Text('Ver historial de pagos'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DatoResumen extends StatelessWidget {
  const _DatoResumen({
    required this.titulo,
    required this.valor,
    this.destacado = false,
  });

  final String titulo;
  final String valor;
  final bool destacado;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(titulo),
          Text(
            valor,
            style: TextStyle(
              fontWeight: destacado ? FontWeight.bold : FontWeight.w600,
              fontSize: destacado ? 17 : null,
            ),
          ),
        ],
      ),
    );
  }
}

class _FacturaCard extends StatelessWidget {
  const _FacturaCard({
    required this.factura,
    required this.token,
    required this.hijo,
    required this.onPagoRegistrado,
  });

  final Factura factura;
  final String token;
  final Hijo hijo;
  final Future<void> Function() onPagoRegistrado;

  @override
  Widget build(BuildContext context) {
    final puedeRegistrarPago = factura.detalles.any(
      (detalle) => (double.tryParse(detalle.saldoDisponiblePago) ?? 0) > 0,
    );

    return Card(
      child: ExpansionTile(
        title: Text(
          '${factura.mesNombre} '
          '${factura.anio}',
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 6),
          child: Text(
            'Estado: '
            '${factura.estadoNombre}\n'
            'Saldo: \$${factura.saldo}',
          ),
        ),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        children: [
          const Divider(),

          _DatoFactura(titulo: 'Total', valor: '\$${factura.total}'),

          _DatoFactura(titulo: 'Pagado', valor: '\$${factura.totalPagado}'),

          _DatoFactura(titulo: 'Saldo', valor: '\$${factura.saldo}'),

          _DatoFactura(titulo: 'Vencimiento', valor: factura.fechaVencimiento),

          const SizedBox(height: 12),

          Align(
            alignment: Alignment.centerLeft,
            child: Text(
              'Conceptos',
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),

          const SizedBox(height: 8),

          ...factura.detalles.map(
            (detalle) => ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text(detalle.descripcion),
              subtitle: Text(detalle.tipoConcepto),
              trailing: Text('\$${detalle.importe}'),
            ),
          ),

          const SizedBox(height: 12),

          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) =>
                        PagosScreen(token: token, hijo: hijo, factura: factura),
                  ),
                );
              },
              icon: const Icon(Icons.payments_outlined),
              label: const Text('Ver pagos y comprobantes'),
            ),
          ),

          if (puedeRegistrarPago) ...[
            const SizedBox(height: 8),

            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: () async {
                  final mensaje = await Navigator.of(context).push<String>(
                    MaterialPageRoute(
                      builder: (_) => RegistrarPagoScreen(
                        token: token,
                        hijo: hijo,
                        factura: factura,
                      ),
                    ),
                  );

                  if (mensaje == null || !context.mounted) {
                    return;
                  }

                  await onPagoRegistrado();

                  if (!context.mounted) {
                    return;
                  }

                  ScaffoldMessenger.of(context)
                      .showSnackBar(SnackBar(content: Text(mensaje)));
                },
                icon: const Icon(Icons.upload_file),
                label: const Text('Registrar transferencia'),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _DatoFactura extends StatelessWidget {
  const _DatoFactura({required this.titulo, required this.valor});

  final String titulo;
  final String valor;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(titulo),
          Text(valor, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}
