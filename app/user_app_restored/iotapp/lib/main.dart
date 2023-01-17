import 'package:flutter/material.dart';
import 'login.dart';
import 'register.dart';
import 'home.dart';
<<<<<<< HEAD
import 'rooms_map.dart';

void main() {
=======
import 'editRoom.dart';

void main() {

>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
  runApp(MaterialApp(
    debugShowCheckedModeBanner: false,
    home: MyLogin(),
    routes: {
      'register': (context) => MyRegister(),
      'login': (context) => MyLogin(),
      'home': (context) => UserHome(),
<<<<<<< HEAD
      'map': (context) => Mappa(),
=======
      'editRoom': (context) => EditRoom(),
      
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
    },
  ));
}
