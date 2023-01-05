class Credentials {
  late String username;
  late String password;
  late String authToken;

  Credentials({required this.username, required this.password});
}

class UserSession {
  late int? id;
  late int? id_edificio;
  late int? id_room;
  late String username;
  late bool logged_in;
  late String? outcome;

  //late DigitalTwin? digitalTwin;

  //List<Building> edificiList;

  UserSession({
    this.id,
    this.id_edificio,
    this.id_room,
    required this.username,
    required this.logged_in,
    this.outcome,
    //required this.edificiList
  });

  factory UserSession.fromJson(dynamic json) {
    return UserSession(
      id: json['id'],
      id_edificio: json['id_edificio'], //da togliere
      id_room: json['id_room'], //da togliere
      username: json['username'],
      logged_in: json['logged_in'], //da togliere SOLO dal json
      outcome: json['outcome'], //da togliere
    );
  }

  @override
  String toString() {
    return '{ ${this.logged_in}, ${this.username}, ${this.outcome}}';
  }
}

class DigitalTwin {
  late int? room_color;
  late int? room_brightness;
  late int? room_temperature;

  DigitalTwin({this.room_color, this.room_brightness, this.room_temperature});

  factory DigitalTwin.fromJson(dynamic json) {
    json = json['digitalTwin'];
    return DigitalTwin(
        room_color: json?['led_actuator'],
        room_brightness: json?['led_brightness'],
        room_temperature: json?['temperature_actuator']);
  }
}
