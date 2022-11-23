class UserSession {
  late int id;
  late int id_edificio;
  late int id_room;
  late String username;
  late String room_color;
  late String room_brightness;
  late String room_temperature;

  UserSession({
    required this.id,
    required this.id_edificio,
    required this.id_room,
    required this.username,
    required this.room_color,
    required this.room_brightness,
    required this.room_temperature,
  });

  factory UserSession.fromJson(Map<String, dynamic> json) {
    return UserSession(
      id: json['id'],
      id_edificio: json['id_edificio'],
      id_room: json['id_room'],
      username: json['username'],
      room_color: json['room_color'],
      room_brightness: json['room_brightness'],
      room_temperature: json['room_temperature'],
    );
  }
}
