import 'dart:convert';
import 'package:http/http.dart' as http;
import 'models.dart';

const IPSERVER = 'http://192.168.1.240:5000/';

class GlobalValues {
  static UserSession? userSession;
  static late DigitalTwin digitalTwin;
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
    GlobalValues.userSession = UserSession.fromJson(jsonDecode(response.body));
    //GlobalValues.digitalTwin = DigitalTwin.fromJson(jsonDecode(response.body));

    //inserisci null exception SE già loggato, non !!!

    GlobalValues.credentials.authToken =
        jsonDecode(response.body)['token'] ?? "";

    if (GlobalValues.userSession!.logged_in != true) {
      GlobalValues.listBuildings = jsonDecode(response.body)['buildings'];
      return "FIRST-LOGIN";
    }

    return 'LOGGED-ALREADY';
  } else {
    return 'FAILED-LOGIN';
  }
}

//@selectRoom
Future<String> sendOccupationRequest(id_building, id_user) async {
  String username = GlobalValues.credentials.username;
  String password = GlobalValues.credentials.password;

  final response = await http.post(
    Uri.parse(IPSERVER + 'selectRoom'),
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
Future<String> freeRoom(id_user) async {
  final response = await http.post(
    Uri.parse(IPSERVER + 'freeRoom'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'FREEROOM-APP',
      'Auth-token': GlobalValues.credentials.authToken,
    },
    body: (jsonEncode({"id_utente": id_user})),
  );

  if (response.statusCode == 200) {
    return "REQUEST-OK";
  } else {
    return ('BAD-REQUEST');
  }
}

//@register
Future<String> registerUser(id_building, id_user) async {
  final response = await http.post(
    Uri.parse(IPSERVER + 'register'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'REGISTER-APP'
    },
    body: (jsonEncode({"id_utente": id_user, "building_id": id_building})),
  );

  if (response.statusCode == 200) {
    return "REQUEST-OK";
  } else {
    return ('BAD-REQUEST');
  }
}

//@update
Future<String> upateRoom(id_building, id_user) async {
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

Future<String> fetchJobs(List<dynamic> jobs) async {
  final response = await http.post(Uri.parse(IPSERVER + 'selectJobs'),
      headers: <String, String>{
        'Content-Type': 'application/json',
        'Content-ID': 'SELECT-JOBS-APP'
      },
      body: '');

  //jobs = response

  if (response.statusCode == 200) {
    return "REQUEST-OK";
  } else {
    return ('BAD-REQUEST');
  }
}
