import 'dart:convert';
import 'package:http/http.dart' as http;
import 'models.dart';

const IPSERVER = 'http://34.199.236.138:5000/';

class GlobalValues {
  static UserSession? userSession;
  static late DigitalTwin digitalTwin =
      DigitalTwin(room_color: '', room_brightness: '', room_temperature: 0);
  static late List<dynamic> listBuildings = [];
  static late WeatherInfo weatherInfo =
      WeatherInfo(ext_temp: '', ext_humidity: '', city_name: '');
  static late Credentials credentials = Credentials(username: '', password: '');
}

//@login
Future<String> fetchUserSession(user, pwd) async {
  try {
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
              } catch (e) {
                print("Errore listBuildings");
              }
            }
            return 'FIRST-LOGIN';
          case 'Active':
            {
              GlobalValues.digitalTwin =
                  DigitalTwin.fromJson(jsonDecode(response.body));

              GlobalValues.userSession =
                  UserSession.fromJson(jsonDecode(response.body));

              GlobalValues.weatherInfo =
                  WeatherInfo.fromJson(jsonDecode(response.body));

              return 'LOGGED-ALREADY';
            }
        }
      }
      return 'WRONG-CREDENTIALS';
    } else {
      return 'FAILED-LOGIN';
    }
  } catch (e) {
    print(e);
    return 'ERRORE-RETE';
  }
}

//@selectRoom
Future<String> sendOccupationRequest(id_building) async {
  String username = GlobalValues.credentials.username;
  String password = GlobalValues.credentials.password;

  try {
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
      GlobalValues.digitalTwin =
          DigitalTwin.fromJson(jsonDecode(response.body));
      GlobalValues.userSession =
          UserSession.fromJson(jsonDecode(response.body));
      GlobalValues.weatherInfo =
          WeatherInfo.fromJson(jsonDecode(response.body));

      return "REQUEST-OK";
    } else {
      return ('BAD-REQUEST');
    }
  } catch (e) {
    return 'ERRORE-RETE';
  }
}

//@logout
Future<String> logout() async {
  try {
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
  } catch (e) {
    return 'ERRORE-RETE';
  }
}

//@freeRoom
Future<String> freeRoom() async {
  try {
    final response = await http.post(
      Uri.parse(IPSERVER + 'freeRoom'),
      headers: <String, String>{
        'Content-Type': 'application/json',
        'Content-ID': 'FREEROOM-APP',
        'Auth-token': GlobalValues.credentials.authToken,
      },
    );

    if (response.statusCode == 200) {
      try {
        GlobalValues.listBuildings = jsonDecode(response.body)['buildings'];
      } catch (e) {
        print("Errore listBuildings");
      }
      return "REQUEST-OK";
    } else {
      return ('BAD-REQUEST');
    }
  } catch (e) {
    return 'ERRORE-RETE';
  }
}

class UpdateReq {
  final String color_val;
  final String brightness_val;
  final int temp_val;

  UpdateReq(this.color_val, this.brightness_val, this.temp_val);

  UpdateReq.fromJson(Map<String, dynamic> json)
      : color_val = json['color_val'],
        brightness_val = json['brightness_val'],
        temp_val = json['temp_val'];

  Map<String, dynamic> toJson() => {
        'color_val': color_val,
        'brightness_val': brightness_val,
        'temp_val': temp_val
      };
}

//@update
Future<String?> changeActuatorRequest(UpdateReq request) async {
  final response = await http.post(
    Uri.parse(IPSERVER + 'update'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'UPDATE-APP',
      'Auth-token': GlobalValues.credentials.authToken,
    },
    body: jsonEncode(request.toJson()),
  );

  if (response.statusCode == 200) {
    GlobalValues.digitalTwin = DigitalTwin.fromJson(jsonDecode(response.body));
  } else {
    throw Exception('Failed to send UPDATE');
  }
}

//@register
Future<String> registerUser(user, pwd, sex, profession, birthDate) async {
  try {
    final response = await http.post(
      Uri.parse(IPSERVER + 'register'),
      headers: <String, String>{
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-ID': 'REGISTER-APP'
      },
      body:
          ('username=$user&password=$pwd&birthday=$birthDate&sex=$sex&profession=$profession'),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body)['msg'];
    } else {
      return ('BAD-REQUEST');
    }
  } catch (e) {
    return 'ERRORE-RETE';
  }
}

//@professions
Future<List<Profession>> fetchJobs() async {
  try {
    final response = await http.get(
      Uri.parse(IPSERVER + 'professions'),
      headers: <String, String>{
        'Content-Type': 'application/json',
        'Content-ID': 'SELECT-JOBS-APP'
      },
    );

    if (response.statusCode == 200) {
      List jsonResponse = json.decode(response.body);
      return jsonResponse.map((job) => Profession.fromJson(job)).toList();
    }
    return [];
  } catch (e) {
    return [];
  }
}
