class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api',
  );

  static const String environment = String.fromEnvironment(
    'APP_ENV',
    defaultValue: 'local',
  );
}