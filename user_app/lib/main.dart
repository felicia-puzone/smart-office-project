import 'package:flutter/material.dart';
import 'login.dart';
import 'register.dart';
import 'home.dart';
import 'editRoom.dart';

void main() {
  runApp(MaterialApp(
    debugShowCheckedModeBanner: false,
    home: MyLogin(),
    routes: {
      'register': (context) => MyRegister(),
      'login': (context) => MyLogin(),
      'home': (context) => UserHome(),
      'editRoom': (context) => EditRoom(),
      
    },
  ));
}
