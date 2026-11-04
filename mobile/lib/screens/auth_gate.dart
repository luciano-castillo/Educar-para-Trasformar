import 'package:flutter/material.dart';

import '../services/session_service.dart';
import 'home_screen.dart';
import 'login_screen.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() {
    return _AuthGateState();
  }
}

class _AuthGateState extends State<AuthGate> {
  final _sessionService = SessionService();

  late Future<String?> _tokenFuture;

  @override
  void initState() {
    super.initState();

    _tokenFuture = _sessionService.obtenerToken();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String?>(
      future: _tokenFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        final token = snapshot.data;

        if (token == null || token.isEmpty) {
          return const LoginScreen();
        }

        return HomeScreen(token: token);
      },
    );
  }
}
