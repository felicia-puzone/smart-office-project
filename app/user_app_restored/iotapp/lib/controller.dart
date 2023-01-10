import 'dart:convert';
import 'package:http/http.dart' as http;
import 'models.dart';

const IPSERVER = 'http://192.168.1.240:5000/';

class GlobalValues {
  static UserSession? userSession;
  static late DigitalTwin digitalTwin =
      DigitalTwin(room_color: '', room_brightness: '', room_temperature: '');
  static late List<dynamic> listBuildings = [];
  static late Credentials credentials = Credentials(username: '', password: '');

  //static late selectedBuildingData;
}

//@login
Future<String> fetchUserSession(user, pwd) async {
//inserisci un try-catch su timeout exception
  final response = await http.post(
    Uri.parse(IPSERVER + 'login'),
    headers: <String, String>{
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-ID': 'LOGIN-APP'
    },
    body: ('username=$user&password=$pwd'),
  );

  if (response.statusCode == 200) {
    if (jsonDecode(response.body)['logged_in'] == true) {
      String outcome = jsonDecode(response.body)['outcome'];

      GlobalValues.userSession =
          UserSession.fromJson(jsonDecode(response.body));

      GlobalValues.credentials.authToken =
          jsonDecode(response.body)['token'] ?? "";

      switch (outcome) {
        case 'Login':
          {
            try {
              GlobalValues.listBuildings =
                  jsonDecode(response.body)['buildings'];
            } catch (e) {}
          }
          return 'FIRST-LOGIN';
        case 'Active':
          {
            GlobalValues.digitalTwin =
                DigitalTwin.fromJson(jsonDecode(response.body));

            GlobalValues.userSession =
                UserSession.fromJson(jsonDecode(response.body));

            return 'LOGGED-ALREADY';
          }
      }
    }
    return 'WRONG-CREDENTIALS';
  } else {
    return 'FAILED-LOGIN';
  }
}

//@selectRoom
Future<String> sendOccupationRequest(id_building) async {
  String username = GlobalValues.credentials.username;
  String password = GlobalValues.credentials.password;

  final response = await http.post(
    Uri.parse(IPSERVER + 'selectRoom'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'SELECT-APP',
      'Auth-token': GlobalValues.credentials.authToken,
    },
    body: (jsonEncode({"building_id": id_building})),
  );

  if (response.statusCode == 200) {
    GlobalValues.digitalTwin = DigitalTwin.fromJson(jsonDecode(response.body));
    GlobalValues.userSession = UserSession.fromJson(jsonDecode(response.body));

    return "REQUEST-OK";
  } else {
    return ('BAD-REQUEST');
  }
}

//@logout
Future<String> logout() async {
  final response = await http.post(
    Uri.parse(IPSERVER + 'logout'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'Logout-APP',
      'Auth-token': GlobalValues.credentials.authToken,
    },
  );

  if (response.statusCode == 200) {
    return 'REQUEST-OK';
  } else {
    return ('BAD-REQUEST');
  }
}

//@freeRoom
Future<String> freeRoom() async {
  final response = await http.post(
    Uri.parse(IPSERVER + 'freeRoom'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'FREEROOM-APP',
      'Auth-token': GlobalValues.credentials.authToken,
    },
    //body: (jsonEncode({"id_utente": id_user})),
  );

  if (response.statusCode == 200) {
    try {
      GlobalValues.listBuildings = jsonDecode(response.body)['buildings'];
    } catch (e) {}
    return "REQUEST-OK";
  } else {
    return ('BAD-REQUEST');
  }
}

//@register
Future<String> registerUser(user, pwd, sex, profession, birthDate) async {
  final response = await http.post(
    Uri.parse(IPSERVER + 'register'),
    headers: <String, String>{
      'Content-Type': 'application/x-www-form-urlencoded',
      // 'Content-ID': 'REGISTER-APP'
    },
    body:
        ('username=$user&password=$pwd&birthday=$birthDate&sex=$sex&profession=$profession'),
  );

  if (response.statusCode == 200) {
    return response.body;
  } else {
    return ('BAD-REQUEST');
  }
}

//@update
Future<String> updateRoom(id_building, id_user) async {
  final response = await http.post(
    Uri.parse(IPSERVER + 'update'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'SELECT-APP',
      'Auth-token': GlobalValues.credentials.authToken,
    },
    body: (jsonEncode({"id_utente": id_user, "building_id": id_building})),
  );

  if (response.statusCode == 200) {
    return "REQUEST-OK";
  } else {
    return ('BAD-REQUEST');
  }
}

Future<List<Profession>> fetchJobs() async {
  final response = await http.get(
    Uri.parse(IPSERVER + 'professions'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'SELECT-JOBS-APP'
    },
  );

  if (response.statusCode == 200) {
    List jsonResponse = json.decode(response.body);
    return jsonResponse.map((job) => new Profession.fromJson(job)).toList();
  }
  return [];
}



////MQTT
