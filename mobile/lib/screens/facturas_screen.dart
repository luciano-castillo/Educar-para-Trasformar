import 'package:flutter/material.dart';

import '../models/factura.dart';
import '../models/hijo.dart';
import '../services/facturas_service.dart';
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

  late Future<List<Factura>> _facturasFuture;

  @override
  void initState() {
    super.initState();

    _facturasFuture = _facturasService.obtenerFacturas(
      token: widget.token,
      idAlumno: widget.hijo.idAlumno,
    );
  }

  Future<void> _recargar() async {
    setState(() {
      _facturasFuture = _facturasService.obtenerFacturas(
        token: widget.token,
        idAlumno: widget.hijo.idAlumno,
      );
    });

    await _facturasFuture;
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

            if (facturas.isEmpty) {
              return ListView(
                children: [
                  const SizedBox(height: 100),
                  const Icon(Icons.receipt_long, size: 70),
                  const SizedBox(height: 16),
                  Text(
                    'No hay facturas para '
                    '${widget.hijo.nombreCompleto}.',
                    textAlign: TextAlign.center,
                  ),
                ],
              );
            }

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
            'Estado: ${factura.estadoNombre}\n'
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
