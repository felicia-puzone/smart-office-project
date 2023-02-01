import 'package:flutter/material.dart';
<<<<<<< HEAD
import 'controller.dart';
import 'home.dart';
import 'package:iotapp/rooms_map.dart';

final userTextController = TextEditingController();
final pwdTextController = TextEditingController();

=======
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


>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
class MyLogin extends StatefulWidget {
  const MyLogin({Key? key}) : super(key: key);

  @override
  _MyLoginState createState() => _MyLoginState();
}

class _MyLoginState extends State<MyLogin> {
<<<<<<< HEAD
  late Future<String> futureUserSession;

  @override
  void initState() {
=======

  
  @override
  void initState() {
    print('INIT CALLED');
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
    super.initState();
  }

  @override
<<<<<<< HEAD
=======
  void dispose() {
    // Clean up the controller when the widget is disposed.
    //userTextController.dispose();
    //pwdTextController.dispose();
    //super.dispose();
  }

  @override
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
<<<<<<< HEAD
                                    onPressed: () async {
                                      String result = await fetchUserSession(
                                          userTextController.text,
                                          pwdTextController.text);
                                      if (result == 'FIRST-LOGIN') {
                                        Navigator.push(
                                            context,
                                            MaterialPageRoute(
                                                builder: (context) =>
                                                    const Mappa()));
                                      } else if (result == 'LOGGED-ALREADY') {
                                        Navigator.push(
                                            context,
                                            MaterialPageRoute(
                                                builder: (context) =>
                                                    const UserHome()));
                                      } else {
                                        showDialog(
                                            context: context,
                                            builder: (ctx) => AlertDialog(
                                                  title: Text(result),
                                                  actions: <Widget>[
                                                    TextButton(
                                                      onPressed: () {
                                                        Navigator.pushNamed(
                                                            context, 'login');
                                                      },
                                                      child: Container(
                                                        padding:
                                                            const EdgeInsets
                                                                .all(14),
                                                        child: const Text("OK"),
                                                      ),
                                                    ),
                                                  ],
                                                ));
                                      }
                                    },
                                    icon: const Icon(
=======
                                    onPressed: () {
                                      
                                      Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                              builder: (context) =>
                                                  UserHome()));
                                    },
                                    icon: Icon(
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
                                      Icons.arrow_forward,
                                    )),
                              ),
                            ],
                          ),
<<<<<<< HEAD
                          const SizedBox(
=======
                          SizedBox(
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
                                      fontSize: 16),
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
                                      fontSize: 16,
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
