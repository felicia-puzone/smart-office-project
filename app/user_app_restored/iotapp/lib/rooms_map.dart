import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/src/widgets/container.dart';
import 'package:flutter/src/widgets/framework.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:iotapp/home.dart';
import 'package:latlong2/latlong.dart';
import 'package:flutter_map_location_marker/flutter_map_location_marker.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

Future<String> sendOccupationRequest(id_building, id_user) async {
  final response = await http.post(
    Uri.parse('http://192.168.1.240:5000/selectRoom'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'SELECT-APP'
    },
    body: (jsonEncode({"id_utente": id_user, "building_id": id_building})),
  );

  if (response.statusCode == 200) {
    return "Stanza occupata con successo";
  } else {
    return ('Occupazione non riuscita. Errore: ' +
        response.statusCode.toString());
  }
}

class BuildingMarker extends StatefulWidget {
  final int? idRoom;
  final String city;
  final String number;
  final String route;

  BuildingMarker({
    super.key,
    required this.idRoom,
    required this.city,
    required this.number,
    required this.route,
  });

  @override
  State<BuildingMarker> createState() => _BuildingMarkerState();
}

class _BuildingMarkerState extends State<BuildingMarker> {
  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      height: 10,
      width: 10,
      duration: const Duration(milliseconds: 2),
      curve: Curves.easeIn,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => showDialog<String>(
            context: context,
            builder: (BuildContext context) => AlertDialog(
              title: Container(
                  child: Text('Nome edificio'), alignment: Alignment.center),
              content: Container(
                  height: 70,
                  child: Column(
                    children: [
                      Text(widget.city +
                          ' ' +
                          widget.route +
                          ', ' +
                          widget.number),
                      Text('Numero stanze disponibili: ' + '..')
                    ],
                  )),
              actions: <Widget>[
                Row(children: [
                  Expanded(
                      child: Container(
                          height: 50,
                          //padding: EdgeInsets.only(top: 35, bottom: 35),
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                                textStyle: const TextStyle(
                                  color: Color(0xff4c505b),
                                  fontSize: 20,
                                ),
                                backgroundColor: Colors.orangeAccent),
                            onPressed: () => sendOccupationRequest(
                                GlobalValues.userSession!.id, widget.idRoom),
                            /*prenotazione*/
                            child: const Text('Prenota'),
                          ))),
                ]),
                Row(
                  children: [
                    Expanded(
                        child: Container(
                            height: 50,
                            //padding: EdgeInsets.only(top: 35, bottom: 35),
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                  textStyle: const TextStyle(
                                    color: Color(0xff4c505b),
                                    fontSize: 20,
                                  ),
                                  backgroundColor: Colors.grey),
                              onPressed: () => Navigator.pop(context),
                              /*prenotazione*/
                              child: const Text('Annulla'),
                            )))
                  ],
                ),
              ],
            ),
          ),
          child: ClipRRect(
            child: Image.asset('assets/marker.png', width: 20, height: 20),
          ),
        ),
      ),
    );
  }
}

class Mappa extends StatefulWidget {
  const Mappa({super.key});

  @override
  State<Mappa> createState() => _MappaState();
}

class _MappaState extends State<Mappa> {
  late Future<Position> _initPosition;
  late List<Marker> _markers;

  @override
  void initState() {
    _initPosition = getLocation();

    _markers = initMarkers();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        body: FutureBuilder<Position>(
            future: _initPosition,
            builder: (context, snapshot) {
              if (snapshot.hasData) {
                return FlutterMap(
                  options: MapOptions(
                    center: LatLng(
                        snapshot.data!.latitude, snapshot.data!.longitude),
                    zoom: 10.2,
                  ),
                  nonRotatedChildren: [
                    AttributionWidget.defaultWidget(
                      source: 'OpenStreetMap contributors',
                      onSourceTapped: null,
                    ),
                  ],
                  children: [
                    TileLayer(
                      urlTemplate:
                          'http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}',
                      userAgentPackageName: 'com.example.app',
                    ),
                    CurrentLocationLayer(),
                    MarkerLayer(markers: _markers),
                  ],
                );
              } else
                return Text("C'è qualquadra che non cosa");
            }));
  }
}

Future<Position> getLocation() async {
  LocationPermission permission;
  permission = await Geolocator.checkPermission();
  permission = await Geolocator.requestPermission();
  if (permission == LocationPermission.denied) {
    //nothing
  }
  Position position = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.low);
  print(position);
  return position;
}

List<Marker> initMarkers() {
  List<Marker> markers = [];

  GlobalValues.listBuildings.forEach((building) {
    markers.add(Marker(
        point: LatLng(
            double.parse(building['lat']), double.parse(building['lon'])),
        builder: (context) => BuildingMarker(
            idRoom: building['id_building'],
            city: building['city'],
            number: building['number'],
            route: building['route'])));
  });

  return markers;
}
