import 'package:flutter/material.dart';

import '../services/session_service.dart';

import '../models/hijo.dart';
import '../services/hijos_service.dart';
import 'facturas_screen.dart';

import '../services/auth_service.dart';
import 'login_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, required this.token});

  final String token;

  @override
  State<HomeScreen> createState() {
    return _HomeScreenState();
  }
}

class _HomeScreenState extends State<HomeScreen> {
  final _hijosService = HijosService();
  final _authService = AuthService();
  final _sessionService = SessionService();
  Future<void> _cerrarSesion() async {
    try {
      await _authService.logout(
        token: widget.token,
      );
    } catch (_) {
      // Aunque el servidor rechace el token,
      // la sesión local debe poder cerrarse.
    }

    await _sessionService.eliminarToken();

    if (!mounted) {
      return;
    }

    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(
        builder: (_) => const LoginScreen(),
      ),
      (route) => false,
    );
  }

  late Future<List<Hijo>> _hijosFuture;

  @override
  void initState() {
    super.initState();

    _hijosFuture = _hijosService.obtenerHijos(token: widget.token);
  }

  Future<void> _recargar() async {
    setState(() {
      _hijosFuture = _hijosService.obtenerHijos(token: widget.token);
    });

    await _hijosFuture;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis hijos'),
        actions: [
          IconButton(
            onPressed: _cerrarSesion,
            tooltip: 'Cerrar sesión',
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _recargar,
        child: FutureBuilder<List<Hijo>>(
          future: _hijosFuture,
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

            final hijos = snapshot.data ?? [];

            if (hijos.isEmpty) {
              return ListView(
                children: const [
                  SizedBox(height: 120),
                  Icon(Icons.family_restroom, size: 64),
                  SizedBox(height: 16),
                  Center(child: Text('No hay alumnos asociados.')),
                ],
              );
            }

            return ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: hijos.length,
              separatorBuilder: (context, index) {
                return const SizedBox(height: 12);
              },
              itemBuilder: (context, index) {
                final hijo = hijos[index];

                return Card(
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16),
                    leading: const CircleAvatar(child: Icon(Icons.school)),
                    title: Text(hijo.nombreCompleto),
                    subtitle: Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        'Legajo: ${hijo.legajo}\n'
                        '${hijo.nivel} - '
                        '${hijo.curso} '
                        '${hijo.division}',
                      ),
                    ),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) =>
                              FacturasScreen(token: widget.token, hijo: hijo),
                        ),
                      );
                    },
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}
