import 'package:flutter/material.dart';
import 'package:flutter/src/widgets/container.dart';
import 'package:flutter/src/widgets/framework.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:flutter_map_location_marker/flutter_map_location_marker.dart';
import 'package:geolocator/geolocator.dart';

class Mappa extends StatefulWidget {
  const Mappa({super.key});

  @override
  State<Mappa> createState() => _MappaState();
}

class _MappaState extends State<Mappa> {
  late Future<Position> _initPosition;
  @override
  void initState() {
    _initPosition = getLocation();
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
