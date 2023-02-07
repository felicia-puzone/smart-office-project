import 'package:flutter/material.dart';
import 'login.dart';
import 'register.dart';
import 'home.dart';
import 'rooms_map.dart';

void main() {
  runApp(MaterialApp(
    debugShowCheckedModeBanner: false,
    home: MyLogin(),
    routes: {
      'register': (context) => MyRegister(),
      'login': (context) => MyLogin(),
      'home': (context) => UserHome(),
      'map': (context) => Mappa(),
    },
  ));
}
