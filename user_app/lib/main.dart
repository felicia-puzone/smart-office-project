import 'package:flutter/material.dart';
import 'login.dart';
import 'register.dart';
import 'home.dart';
import 'editRoom.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

void main() {
    final GoogleMapsFlutterPlatform mapsImplementation =
      GoogleMapsFlutterPlatform.instance;
  if (mapsImplementation is GoogleMapsFlutterAndroid) {
    mapsImplementation.useAndroidViewSurface = true;
  }
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
