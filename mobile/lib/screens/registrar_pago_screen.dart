import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../models/factura.dart';
import '../models/hijo.dart';
import '../services/pagos_service.dart';

class RegistrarPagoScreen extends StatefulWidget {
  const RegistrarPagoScreen({
    super.key,
    required this.token,
    required this.hijo,
    required this.factura,
  });

  final String token;
  final Hijo hijo;
  final Factura factura;

  @override
  State<RegistrarPagoScreen> createState() {
    return _RegistrarPagoScreenState();
  }
}

class _RegistrarPagoScreenState extends State<RegistrarPagoScreen> {
  final _pagosService = PagosService();

  final _numeroOperacionController = TextEditingController();

  final _observacionesController = TextEditingController();

  final Set<int> _seleccionados = {};

  final Map<int, TextEditingController> _importeControllers = {};

  List<PlatformFile> _comprobantes = [];

  DateTime _fechaTransferencia = DateTime.now();

  bool _enviando = false;

  List<DetalleFactura> get _conceptosDisponibles {
    return widget.factura.detalles
        .where(
          (detalle) => (double.tryParse(detalle.saldoDisponiblePago) ?? 0) > 0,
        )
        .toList();
  }

  @override
  void initState() {
    super.initState();

    for (final detalle in _conceptosDisponibles) {
      _importeControllers[detalle.idDetalle] = TextEditingController(
        text: detalle.saldoDisponiblePago,
      );
    }
  }

  @override
  void dispose() {
    _numeroOperacionController.dispose();
    _observacionesController.dispose();

    for (final controller in _importeControllers.values) {
      controller.dispose();
    }

    super.dispose();
  }

  String _formatearFecha(DateTime fecha) {
    final dia = fecha.day.toString().padLeft(2, '0');

    final mes = fecha.month.toString().padLeft(2, '0');

    return '$dia/$mes/${fecha.year}';
  }

  Future<void> _seleccionarFecha() async {
    final fecha = await showDatePicker(
      context: context,
      initialDate: _fechaTransferencia,
      firstDate: DateTime(DateTime.now().year - 1),
      lastDate: DateTime.now(),
    );

    if (fecha == null || !mounted) {
      return;
    }

    setState(() {
      _fechaTransferencia = fecha;
    });
  }

  Future<void> _seleccionarComprobantes() async {
    final archivos = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png'],
    );

    if (!mounted) {
      return;
    }

    if (archivos.isNotEmpty) {
      setState(() {
        _comprobantes = archivos;
      });
    }
  }

  void _mostrarError(String mensaje) {
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text(mensaje)));
  }

  Future<void> _enviarPago() async {
    if (_seleccionados.isEmpty) {
      _mostrarError('Seleccione al menos un concepto.');

      return;
    }

    if (_comprobantes.isEmpty) {
      _mostrarError('Adjunte al menos un comprobante.');

      return;
    }

    final aplicaciones = <Map<String, dynamic>>[];

    for (final detalle in _conceptosDisponibles) {
      if (!_seleccionados.contains(detalle.idDetalle)) {
        continue;
      }

      final controller = _importeControllers[detalle.idDetalle];

      final texto = controller!.text.trim().replaceAll(',', '.');

      final importe = double.tryParse(texto);

      final disponible = double.tryParse(detalle.saldoDisponiblePago) ?? 0;

      if (importe == null || importe <= 0) {
        _mostrarError(
          'Ingrese un importe válido para '
          '${detalle.descripcion}.',
        );

        return;
      }

      if (importe > disponible) {
        _mostrarError(
          'El importe de '
          '${detalle.descripcion} '
          'supera el saldo disponible.',
        );

        return;
      }

      aplicaciones.add({'id_detalle': detalle.idDetalle, 'importe': texto});
    }

    setState(() {
      _enviando = true;
    });

    try {
      final mensaje = await _pagosService.registrarPago(
        token: widget.token,
        idAlumno: widget.hijo.idAlumno,
        idFactura: widget.factura.idFactura,
        fechaTransferencia: _fechaTransferencia,
        aplicaciones: aplicaciones,
        comprobantes: _comprobantes,
        numeroOperacion: _numeroOperacionController.text.trim(),
        observaciones: _observacionesController.text.trim(),
      );

      if (!mounted) {
        return;
      }

      Navigator.of(context).pop(mensaje);
    } catch (error) {
      if (!mounted) {
        return;
      }

      _mostrarError(error.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) {
        setState(() {
          _enviando = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Registrar transferencia')),
      body: ListView(
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
          const SizedBox(height: 24),

          ListTile(
            contentPadding: EdgeInsets.zero,
            leading: const Icon(Icons.calendar_month),
            title: const Text('Fecha de transferencia'),
            subtitle: Text(_formatearFecha(_fechaTransferencia)),
            trailing: const Icon(Icons.edit),
            onTap: _seleccionarFecha,
          ),

          const Divider(),

          Text(
            'Conceptos a pagar',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),

          if (_conceptosDisponibles.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 20),
              child: Text(
                'No hay conceptos '
                'disponibles para pagar.',
              ),
            ),

          ..._conceptosDisponibles.map((detalle) {
            final seleccionado = _seleccionados.contains(detalle.idDetalle);

            return Card(
              child: Column(
                children: [
                  CheckboxListTile(
                    value: seleccionado,
                    title: Text(detalle.descripcion),
                    subtitle: Text(
                      'Disponible: '
                      '\$${detalle.saldoDisponiblePago}',
                    ),
                    onChanged: (valor) {
                      setState(() {
                        if (valor == true) {
                          _seleccionados.add(detalle.idDetalle);
                        } else {
                          _seleccionados.remove(detalle.idDetalle);
                        }
                      });
                    },
                  ),

                  if (seleccionado)
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                      child: TextField(
                        controller: _importeControllers[detalle.idDetalle],
                        keyboardType: const TextInputType.numberWithOptions(
                          decimal: true,
                        ),
                        decoration: const InputDecoration(
                          labelText: 'Importe a pagar',
                          prefixText: '\$ ',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                ],
              ),
            );
          }),

          const SizedBox(height: 16),

          TextField(
            controller: _numeroOperacionController,
            decoration: const InputDecoration(
              labelText: 'Número de operación',
              border: OutlineInputBorder(),
            ),
          ),

          const SizedBox(height: 16),

          TextField(
            controller: _observacionesController,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'Observaciones',
              border: OutlineInputBorder(),
            ),
          ),

          const SizedBox(height: 24),

          OutlinedButton.icon(
            onPressed: _seleccionarComprobantes,
            icon: const Icon(Icons.attach_file),
            label: const Text('Seleccionar comprobantes'),
          ),

          const SizedBox(height: 8),

          if (_comprobantes.isEmpty)
            const Text(
              'Ningún archivo seleccionado.',
              textAlign: TextAlign.center,
            ),

          ..._comprobantes.map(
            (archivo) => ListTile(
              leading: const Icon(Icons.description_outlined),
              title: Text(archivo.name),
            ),
          ),

          const SizedBox(height: 24),

          FilledButton.icon(
            onPressed: _enviando || _conceptosDisponibles.isEmpty
                ? null
                : _enviarPago,
            icon: _enviando
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.send),
            label: Text(_enviando ? 'Enviando...' : 'Registrar pago'),
          ),
        ],
      ),
    );
  }
}
