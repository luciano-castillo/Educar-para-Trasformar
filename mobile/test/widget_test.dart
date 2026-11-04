import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/screens/login_screen.dart';

void main() {
  testWidgets('muestra la pantalla de inicio de sesión', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MaterialApp(home: LoginScreen()));

    expect(find.text('Educar Para Transformar'), findsOneWidget);

    expect(find.text('Usuario'), findsOneWidget);

    expect(find.text('Contraseña'), findsOneWidget);

    expect(find.text('Iniciar sesión'), findsOneWidget);
  });
}
