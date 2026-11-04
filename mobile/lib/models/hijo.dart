class Hijo {
  const Hijo({
    required this.idAlumno,
    required this.nombre,
    required this.apellido,
    required this.legajo,
    required this.curso,
    required this.division,
    required this.turno,
    required this.nivel,
  });

  final int idAlumno;
  final String nombre;
  final String apellido;
  final String legajo;
  final String curso;
  final String division;
  final String turno;
  final String nivel;

  factory Hijo.fromJson(Map<String, dynamic> json) {
    final cursoData = json['curso'] as Map<String, dynamic>?;

    return Hijo(
      idAlumno: json['id_alumno'] as int,
      nombre: json['nombre'] as String,
      apellido: json['apellido'] as String,
      legajo: json['legajo'] as String,
      curso: cursoData?['nombre'] as String? ?? '',
      division: cursoData?['division'] as String? ?? '',
      turno: cursoData?['turno'] as String? ?? '',
      nivel: cursoData?['nivel'] as String? ?? '',
    );
  }

  String get nombreCompleto {
    return '$apellido, $nombre';
  }
}
