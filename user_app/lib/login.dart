import 'package:flutter/material.dart';
import 'package:loginuicolors/edificio.dart';
import 'register.dart';
import 'main.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'home.dart';
import 'userSession.dart';
import 'edificio.dart';

//////////////// REQUEST
final userTextController = TextEditingController();
final pwdTextController = TextEditingController();

var userSession;

Future<String> fetchUserSession() async {
  String user = userTextController.text;
  String pwd = pwdTextController.text;

  final response = await http.post(
    Uri.parse('http://192.168.180.91:5000/loginapp'),
    headers: <String, String>{
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-ID': 'LOGIN-APP'
    },
    body: ('username=$user&password=$pwd'),
  );

  if (response.statusCode == 200) {
    // If the server did return a 200 OK response,
    // then parse the JSON.
    userSession = UserSession.fromJson(jsonDecode(response.body));

    return userSession.username;
  } else {
    // If the server did not return a 200 OK response,
    // then throw an exception.
    throw Exception('Failed to load UserSession');
  }
}

class UserSessionResponse extends StatefulWidget {
  const UserSessionResponse({super.key});

  @override
  State<UserSessionResponse> createState() => _UserSessionResponseState();
}

class _UserSessionResponseState extends State<UserSessionResponse> {
  //late Future<UserSession> futureUserSession;
  late Future<String> provaResponse;

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: const Text('Risposta'),
        ),
        body: SingleChildScrollView(
          child: FutureBuilder<String>(
            future: provaResponse,
            builder: (context, snapshot) {
              if (snapshot.hasData) {
                /*return Text(snapshot.data!.name +
                ' ' +
                snapshot.data!.email +
                ' ' +
                snapshot.data!.gender); */
                return Text(snapshot.data!);
              } else if (snapshot.hasError) {
                return Text('${snapshot.error}');
              }

              // By default, show a loading spinner.
              return const CircularProgressIndicator();
            },
          ),
        ));
  }
}

/////////////////////////////////////////////////
///
///
///

class EdificiResponse extends StatefulWidget {
  const EdificiResponse({super.key});

  @override
  State<EdificiResponse> createState() => _EdificiResponseState();
}

class _EdificiResponseState extends State<EdificiResponse> {
  //late Future<UserSession> futureUserSession;
  late Future<String> edificiResponse;

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: const Text('Risposta'),
        ),
        body: SingleChildScrollView(
          child: FutureBuilder<String>(
            future: edificiResponse,
            builder: (context, snapshot) {
              if (snapshot.hasData) {
                /*return Text(snapshot.data!.name +
                ' ' +
                snapshot.data!.email +
                ' ' +
                snapshot.data!.gender); */
                return Text(snapshot.data!);
              } else if (snapshot.hasError) {
                return Text('${snapshot.error}');
              }

              // By default, show a loading spinner.
              return const CircularProgressIndicator();
            },
          ),
        ));
  }
}

const List<String> list = <String>['One', 'Two', 'Three', 'Four'];

class MyLogin extends StatefulWidget {
  const MyLogin({Key? key}) : super(key: key);

  @override
  _MyLoginState createState() => _MyLoginState();
}

class _MyLoginState extends State<MyLogin> {
  String dropdownValue = list.first;
  late Future<Edificio> futureEfici;

  @override
  void initState() {
    print('INIT CALLED');
    super.initState();
  }

  @override
  void dispose() {
    // Clean up the controller when the widget is disposed.
    userTextController.dispose();
    pwdTextController.dispose();
    super.dispose();
  }


  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        image: DecorationImage(
            image: AssetImage('assets/login.png'), fit: BoxFit.cover),
      ),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: Stack(
          children: [
            Container(
              padding: EdgeInsets.only(left: 35, top: 130),
              child: Text(
                'SMART OFFICE',
                style: TextStyle(color: Colors.black, fontSize: 45),
              ),
            ),
            SingleChildScrollView(
              child: Container(
                padding: EdgeInsets.only(
                    top: MediaQuery.of(context).size.height * 0.5),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      margin: EdgeInsets.only(left: 35, right: 35),
                      child: Column(
                        children: [
                          TextField(
                            controller: userTextController,
                            style: TextStyle(color: Colors.black),
                            decoration: InputDecoration(
                                fillColor: Colors.grey.shade100,
                                filled: true,
                                hintText: "Username",
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(10),
                                )),
                          ),
                          SizedBox(
                            height: 30,
                          ),
                          TextField(
                            controller: pwdTextController,
                            style: TextStyle(),
                            obscureText: true,
                            decoration: InputDecoration(
                                fillColor: Colors.grey.shade100,
                                filled: true,
                                hintText: "Password",
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(10),
                                )),
                          ),
                          SizedBox(
                            height: 40,
                          ),
                          Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Expanded(
                                    child: Container(
                                        padding: EdgeInsets.only(
                                            top: 20, bottom: 20),
                                        child: DropdownButton<String>(
                                          value: dropdownValue,
                                          icon:
                                              const Icon(Icons.arrow_downward),
                                          elevation: 20,
                                          hint: (Text("Seleziona un edificio")),
                                          style: const TextStyle(
                                            color: Colors.black,
                                          ),
                                          underline: Container(
                                            height: 2,
                                            color: Colors.cyan,
                                          ),
                                          onChanged: (String? value) {
                                            // This is called when the user selects an item.
                                            setState(() {
                                              dropdownValue = value!;
                                            });
                                          },
                                          items: list
                                              .map<DropdownMenuItem<String>>(
                                                  (String value) {
                                            return DropdownMenuItem<String>(
                                              value: value,
                                              child: Text(value),
                                            );
                                          }).toList(),
                                        )))
                              ]),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Accedi',
                                style: TextStyle(
                                    fontSize: 27, fontWeight: FontWeight.w700),
                              ),
                              CircleAvatar(
                                radius: 30,
                                backgroundColor: Color(0xff4c505b),
                                child: IconButton(
                                    color: Colors.white,
                                    onPressed: () {
                                      Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                              builder: (context) =>
                                                  EdificiResponse()));
                                    },
                                    icon: Icon(
                                      Icons.arrow_forward,
                                    )),
                              ),
                            ],
                          ),
                          SizedBox(
                            height: 40,
                          ),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              TextButton(
                                onPressed: () {
                                  Navigator.pushNamed(context, 'register');
                                },
                                child: Text(
                                  'Registrazione',
                                  textAlign: TextAlign.left,
                                  style: TextStyle(
                                      decoration: TextDecoration.underline,
                                      color: Color(0xff4c505b),
                                      fontSize: 18),
                                ),
                                style: ButtonStyle(),
                              ),
                              TextButton(
                                  onPressed: () {},
                                  child: Text(
                                    'Password dimenticata?',
                                    style: TextStyle(
                                      decoration: TextDecoration.underline,
                                      color: Color(0xff4c505b),
                                      fontSize: 18,
                                    ),
                                  )),
                            ],
                          ),
                          Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Expanded(
                                    child: Container(
                                  padding: EdgeInsets.only(top: 35, bottom: 35),
                                  height: 150,
                                  child: ElevatedButton(
                                      style: ElevatedButton.styleFrom(
                                          textStyle: const TextStyle(
                                            color: Color(0xff4c505b),
                                            fontSize: 20,
                                          ),
                                          backgroundColor: Colors.orangeAccent),
                                      onPressed: () {},
                                      child: const Text('Login with FaceID')),
                                ))
                              ]),
                        ],
                      ),
                    )
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
