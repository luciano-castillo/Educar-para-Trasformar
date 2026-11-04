import 'package:flutter/material.dart';

import 'screens/auth_gate.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  runApp(const EducarApp());
}

class EducarApp extends StatelessWidget {
  const EducarApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Educar Para Transformar',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
      ),
      home: const AuthGate(),
    );
  }
}
