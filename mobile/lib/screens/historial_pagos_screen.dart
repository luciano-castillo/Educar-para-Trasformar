import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/hijo.dart';
import '../models/pago.dart';
import '../services/pagos_service.dart';

class HistorialPagosScreen extends StatefulWidget {
  const HistorialPagosScreen({
    super.key,
    required this.token,
    required this.hijo,
  });

  final String token;
  final Hijo hijo;

  @override
  State<HistorialPagosScreen> createState() {
    return _HistorialPagosScreenState();
  }
}

class _HistorialPagosScreenState extends State<HistorialPagosScreen> {
  final _pagosService = PagosService();

  late Future<List<Pago>> _pagosFuture;

  @override
  void initState() {
    super.initState();

    _cargarPagos();
  }

  void _cargarPagos() {
    _pagosFuture = _pagosService.obtenerHistorialPagos(
      token: widget.token,
      idAlumno: widget.hijo.idAlumno,
    );
  }

  Future<void> _recargar() async {
    setState(() {
      _cargarPagos();
    });

    await _pagosFuture;
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
      appBar: AppBar(title: const Text('Historial de pagos')),
      body: RefreshIndicator(
        onRefresh: _recargar,
        child: FutureBuilder<List<Pago>>(
          future: _pagosFuture,
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

            final pagos = snapshot.data ?? [];

            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text(
                  widget.hijo.nombreCompleto,
                  style: Theme.of(context).textTheme.titleLarge,
                ),

                const SizedBox(height: 4),

                Text(
                  'Legajo: '
                  '${widget.hijo.legajo}',
                ),

                const SizedBox(height: 20),

                if (pagos.isEmpty) ...[
                  const SizedBox(height: 60),
                  const Icon(Icons.payments_outlined, size: 70),
                  const SizedBox(height: 16),
                  const Text(
                    'No hay pagos registrados.',
                    textAlign: TextAlign.center,
                  ),
                ],

                ...pagos.map(
                  (pago) => Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: Card(
                      child: ExpansionTile(
                        title: Text(
                          '${pago.mesNombre} '
                          '${pago.anio}',
                        ),
                        subtitle: Padding(
                          padding: const EdgeInsets.only(top: 6),
                          child: Text(
                            'Monto: '
                            '\$${pago.monto}\n'
                            'Estado: '
                            '${pago.estadoNombre}',
                          ),
                        ),
                        childrenPadding: const EdgeInsets.fromLTRB(
                          16,
                          0,
                          16,
                          16,
                        ),
                        children: [
                          const Divider(),

                          _DatoHistorial(
                            titulo: 'N.º de pago',
                            valor: '#${pago.idPago}',
                          ),

                          _DatoHistorial(
                            titulo: 'Factura',
                            valor: '#${pago.idFactura}',
                          ),

                          _DatoHistorial(
                            titulo: 'Transferencia',
                            valor: pago.fechaTransferencia,
                          ),

                          _DatoHistorial(
                            titulo: 'Monto',
                            valor: '\$${pago.monto}',
                          ),

                          _DatoHistorial(
                            titulo: 'Estado',
                            valor: pago.estadoNombre,
                          ),

                          if (pago.numeroOperacion.isNotEmpty)
                            _DatoHistorial(
                              titulo: 'N.º de operación',
                              valor: pago.numeroOperacion,
                            ),

                          if (pago.observaciones.isNotEmpty)
                            _DatoHistorial(
                              titulo: 'Observaciones',
                              valor: pago.observaciones,
                            ),

                          const Divider(height: 28),

                          Align(
                            alignment: Alignment.centerLeft,
                            child: Text(
                              'Conceptos pagados',
                              style: Theme.of(context).textTheme.titleSmall,
                            ),
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

                          Align(
                            alignment: Alignment.centerLeft,
                            child: Text(
                              'Comprobantes',
                              style: Theme.of(context).textTheme.titleSmall,
                            ),
                          ),

                          const SizedBox(height: 8),

                          if (pago.comprobantes.isEmpty)
                            const Align(
                              alignment: Alignment.centerLeft,
                              child: Text(
                                'Sin comprobantes '
                                'adjuntos.',
                              ),
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
              ],
            );
          },
        ),
      ),
    );
  }
}

class _DatoHistorial extends StatelessWidget {
  const _DatoHistorial({required this.titulo, required this.valor});

  final String titulo;
  final String valor;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
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
