class UserSession {
  late int? id;
  late int? id_edificio;
  late int? id_room;
  late String? username;
  late bool logged_in;
  late String? outcome;

  late DigitalTwin? digitalTwin;

  //List<Building> edificiList;

  UserSession({
    this.id,
    this.id_edificio,
    this.id_room,
    this.username,
    required this.logged_in,
    this.outcome,
    this.digitalTwin,
    //required this.edificiList
  });

  factory UserSession.fromJson(dynamic json) {
    return UserSession(
        id: json['id'],
        id_edificio: json['id_edificio'],
        id_room: json['id_room'],
        username: json['username'],
        logged_in: json['logged_in'],
        outcome: json['outcome'],
        digitalTwin: DigitalTwin?.fromJson(json['digitalTwin']));
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
    return DigitalTwin(
        room_color: json?['led_actuator'],
        room_brightness: json?['led_brightness'],
        room_temperature: json?['temperature_actuator']);
  }
}

class Building {
  late int? id_building;
  late String? address;

  Building({required this.id_building, required this.address});

  factory Building.fromJson(dynamic json) {
    return Building(id_building: json['id_building'], address: json['city']);
  }
}
