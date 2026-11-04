import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/factura.dart';
import '../models/hijo.dart';
import '../models/pago.dart';
import '../services/pagos_service.dart';

class PagosScreen extends StatefulWidget {
  const PagosScreen({
    super.key,
    required this.token,
    required this.hijo,
    required this.factura,
  });

  final String token;
  final Hijo hijo;
  final Factura factura;

  @override
  State<PagosScreen> createState() {
    return _PagosScreenState();
  }
}

class _PagosScreenState extends State<PagosScreen> {
  final _pagosService = PagosService();

  late Future<List<Pago>> _pagosFuture;

  @override
  void initState() {
    super.initState();

    _pagosFuture = _pagosService.obtenerPagos(
      token: widget.token,
      idAlumno: widget.hijo.idAlumno,
      idFactura: widget.factura.idFactura,
    );
  }

  Future<void> _abrirComprobante(String url) async {
    final uri = Uri.parse(url);

    final abierto = await launchUrl(uri, mode: LaunchMode.externalApplication);

    if (!abierto && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No se pudo abrir el comprobante.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pagos y comprobantes')),
      body: FutureBuilder<List<Pago>>(
        future: _pagosFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text(
                  snapshot.error.toString().replaceFirst('Exception: ', ''),
                  textAlign: TextAlign.center,
                ),
              ),
            );
          }

          final pagos = snapshot.data ?? [];

          if (pagos.isEmpty) {
            return const Center(
              child: Text(
                'No hay pagos registrados '
                'para esta factura.',
              ),
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
              Text(
                '${widget.factura.mesNombre} '
                '${widget.factura.anio}',
              ),
              const SizedBox(height: 20),

              ...pagos.map(
                (pago) => Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Pago #${pago.idPago}',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 12),

                          _DatoPago(titulo: 'Estado', valor: pago.estadoNombre),
                          _DatoPago(titulo: 'Monto', valor: '\$${pago.monto}'),
                          _DatoPago(
                            titulo: 'Transferencia',
                            valor: pago.fechaTransferencia,
                          ),

                          if (pago.numeroOperacion.isNotEmpty)
                            _DatoPago(
                              titulo: 'N.º de operación',
                              valor: pago.numeroOperacion,
                            ),

                          if (pago.observaciones.isNotEmpty)
                            _DatoPago(
                              titulo: 'Observaciones',
                              valor: pago.observaciones,
                            ),

                          const Divider(height: 28),

                          Text(
                            'Conceptos pagados',
                            style: Theme.of(context).textTheme.titleSmall,
                          ),
                          const SizedBox(height: 8),

                          ...pago.detalles.map(
                            (detalle) => ListTile(
                              contentPadding: EdgeInsets.zero,
                              title: Text(detalle.concepto),
                              trailing: Text('\$${detalle.importeAplicado}'),
                            ),
                          ),

                          const Divider(height: 28),

                          Text(
                            'Comprobantes',
                            style: Theme.of(context).textTheme.titleSmall,
                          ),
                          const SizedBox(height: 8),

                          if (pago.comprobantes.isEmpty)
                            const Text(
                              'Sin comprobantes '
                              'adjuntos.',
                            ),

                          ...pago.comprobantes.map(
                            (comprobante) => ListTile(
                              contentPadding: EdgeInsets.zero,
                              leading: const Icon(Icons.description_outlined),
                              title: const Text('Ver comprobante'),
                              subtitle: Text(comprobante.fechaSubida),
                              trailing: const Icon(Icons.open_in_new),
                              onTap: comprobante.archivoUrl.isEmpty
                                  ? null
                                  : () {
                                      _abrirComprobante(comprobante.archivoUrl);
                                    },
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _DatoPago extends StatelessWidget {
  const _DatoPago({required this.titulo, required this.valor});

  final String titulo;
  final String valor;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(child: Text(titulo)),
          Expanded(
            child: Text(
              valor,
              textAlign: TextAlign.end,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }
}
