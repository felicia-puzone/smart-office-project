import 'package:flutter/material.dart';
import 'userSession.dart';
import 'login.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_emoji/flutter_emoji.dart';

class GlobalValues {
  static UserSession? userSession;
}

Future<UserSession?> fetchUserSession() async {
  String user = userTextController.text;
  String pwd = pwdTextController.text;

  final response = await http.post(
    Uri.parse('http://155.185.74.161:5000/login'),
    headers: <String, String>{
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-ID': 'LOGIN-APP'
    },
    body: ('username=$user&password=$pwd'),
  );

  if (response.statusCode == 200) {
    // If the server did return a 200 OK response,
    // then parse the JSON.
    GlobalValues.userSession = UserSession.fromJson(jsonDecode(response.body));

    return GlobalValues.userSession;
  } else {
    // If the server did not return a 200 OK response,
    // then throw an exception.
    throw Exception('Failed to load UserSession');
  }
}

class UserHome extends StatefulWidget {
  const UserHome({super.key});

  @override
  State<UserHome> createState() => _UserHomeState();
}

class _UserHomeState extends State<UserHome> {
  late Future<UserSession?> futureUserSession;

  @override
  void initState() {
    super.initState();

    futureUserSession = fetchUserSession();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
        decoration: BoxDecoration(
          image: DecorationImage(
              image: AssetImage('assets/register.png'), fit: BoxFit.cover),
        ),
        child: Scaffold(
            backgroundColor: Colors.transparent,
            body:
                 FutureBuilder<UserSession?>(
                  future: futureUserSession,
                  builder: (context, snapshot) {
                    if (snapshot.hasData) {
                      if (snapshot.data!.logged_in == true) {
                        return Center(
                                child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      const SizedBox(
                                      height: 90,
                                    ),
                              Container(
                                  margin: const EdgeInsets.only(
                                      left: 35, right: 35),
                                  child: Column(children: [
                                    Container(
                                        child: Text(
                                          'Benvenuto ' +
                                              GlobalValues.userSession!.username
                                                  .toString() +
                                              '! 🖖',
                                          style: const TextStyle(
                                              color: Colors.black,
                                              fontSize: 27),
                                        ),
                                        decoration: BoxDecoration(
                                            color: Colors.grey.shade100,
                                            borderRadius:
                                                BorderRadius.circular(5)),
                                        padding: const EdgeInsets.all(8.0)),
                                    const SizedBox(
                                      height: 30,
                                    )
                                  ]))
                            ]));
                      }

                      ////////////////////////
                      ///////////////////////

                      else if (snapshot.data!.logged_in == false) {
                        return AlertDialog(
                          title: const Text('Login Fallito'),
                          alignment: Alignment.center,
                          actions: <Widget>[
                            TextButton(
                              onPressed: () => Navigator.pop(context, 'OK'),
                              child: const Text('OK'),
                            ),
                          ],
                        );
                      }
                    } else if (snapshot.hasError) {
                      return Text('${snapshot.error}');
                    }

                    // By default, show a loading spinner.
                    return const CircularProgressIndicator();
                  },
                ),
              )
            );
  }
}
