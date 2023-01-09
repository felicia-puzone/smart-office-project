class Credentials {
  late String username;
  late String password;
  late String authToken;

  Credentials({required this.username, required this.password});
}

class UserSession {
  late int? id_edificio;
  late int? id_room;
  late String username;

  //late DigitalTwin? digitalTwin;

  //List<Building> edificiList;

  UserSession({
    this.id_edificio,
    this.id_room,
    required this.username,
    //required this.edificiList
  });

  factory UserSession.fromJson(dynamic json) {
    return UserSession(
      id_edificio: json['id_edificio'],
      id_room: json['id_room'],
      username: json['username'],
    );
  }
}

class DigitalTwin {
  var room_color;
  var room_brightness;
  var room_temperature;

  DigitalTwin(
      {required this.room_color,
      required this.room_brightness,
      required this.room_temperature});

  factory DigitalTwin.fromJson(dynamic json) {
    json = json['digitalTwin'];
    return DigitalTwin(
        room_color: json?['room_color'],
        room_brightness: json?['room_temperature'],
        room_temperature: json?['room_brightness']);
  }
}
