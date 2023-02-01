class Edificio {
  int id_edificio;
  String name;

  Edificio({
    required this.id_edificio,
    required this.name,
  });

  factory Edificio.fromJson(Map<String, dynamic> json) {
    return Edificio(
      id_edificio: json['id_building'],
      name: json['city'],
    );
  }
}
