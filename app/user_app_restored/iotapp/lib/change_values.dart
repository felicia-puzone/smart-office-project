import 'package:flutter/material.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';

import 'package:http/http.dart' as http;
import 'dart:async';
import 'dart:convert';
import 'controller.dart';
import 'models.dart';

ValueNotifier<DigitalTwin> digitalTwinValue =
    ValueNotifier<DigitalTwin>(GlobalValues.digitalTwin);

class UpdateReq {
  final String color_val;
  final String brightness_val;
  final String temp_val;

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

Future<String?> changeActuatorRequest(UpdateReq request) async {
  final response = await http.post(
    Uri.parse('http://192.168.1.240:5000/update'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'UPDATE-APP',
      'Auth-token': GlobalValues.credentials.authToken,
    },
    body: jsonEncode(request.toJson()),
  );

  if (response.statusCode == 200) {
    GlobalValues.digitalTwin = DigitalTwin.fromJson(jsonDecode(response.body));
    digitalTwinValue.value = GlobalValues.digitalTwin;
  } else {
    // If the server did not return a 200 OK response,
    // then throw an exception.
    throw Exception('Failed to send UPDATE');
  }
}

class ColorChanger extends StatefulWidget {
  final MqttServerClient client;
  const ColorChanger({super.key, required this.client});

  @override
  State<ColorChanger> createState() => _ColorChangerState();
}

class _ColorChangerState extends State<ColorChanger> {
  @override
  Widget build(BuildContext context) {
    return Container(
        child: Scaffold(
            backgroundColor: Colors.grey.shade100,
            appBar: AppBar(
              title: const Text('Scegli il colore della luce'),
            ),
            body: GridView.count(
              primary: false,
              padding: const EdgeInsets.all(20),
              crossAxisSpacing: 10,
              mainAxisSpacing: 10,
              crossAxisCount: 2,
              children: <Widget>[
                ElevatedButton(
                    style:
                        ElevatedButton.styleFrom(backgroundColor: Colors.red),
                    onPressed: () {
                      changeActuatorRequest(new UpdateReq(
                          'RED',
                          GlobalValues.digitalTwin.room_brightness.toString(),
                          GlobalValues.digitalTwin.room_temperature
                              .toString()));
                    },
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange),
                    onPressed: () {
                      changeActuatorRequest(new UpdateReq(
                          'ORANGE',
                          GlobalValues.digitalTwin.room_brightness.toString(),
                          GlobalValues.digitalTwin.room_temperature
                              .toString()));
                    },
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.yellow),
                    onPressed: () {
                      changeActuatorRequest(new UpdateReq(
                          'YELLOW',
                          GlobalValues.digitalTwin.room_brightness,
                          GlobalValues.digitalTwin.room_temperature));
                    },
                    child: const Text(' ')),
                ElevatedButton(
                    style:
                        ElevatedButton.styleFrom(backgroundColor: Colors.green),
                    onPressed: () {
                      changeActuatorRequest(new UpdateReq(
                          'GREEN',
                          GlobalValues.digitalTwin.room_brightness,
                          GlobalValues.digitalTwin.room_temperature));
                    },
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.tealAccent),
                    onPressed: () {
                      changeActuatorRequest(new UpdateReq(
                          'TEAL',
                          GlobalValues.digitalTwin.room_brightness,
                          GlobalValues.digitalTwin.room_temperature));
                    },
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.lightBlue),
                    onPressed: () {
                      changeActuatorRequest(new UpdateReq(
                          'BLUE',
                          GlobalValues.digitalTwin.room_brightness,
                          GlobalValues.digitalTwin.room_temperature));
                    },
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.indigo),
                    onPressed: () {
                      changeActuatorRequest(new UpdateReq(
                          'INDIGO',
                          GlobalValues.digitalTwin.room_brightness,
                          GlobalValues.digitalTwin.room_temperature));
                    },
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.purple),
                    onPressed: () {
                      changeActuatorRequest(new UpdateReq(
                          'VIOLET',
                          GlobalValues.digitalTwin.room_brightness,
                          GlobalValues.digitalTwin.room_temperature));
                    },
                    child: const Text(' ')),
                ElevatedButton(
                    style:
                        ElevatedButton.styleFrom(backgroundColor: Colors.grey),
                    onPressed: () {
                      changeActuatorRequest(new UpdateReq(
                          'RAINBOW',
                          GlobalValues.digitalTwin.room_brightness,
                          GlobalValues.digitalTwin.room_temperature));
                    },
                    child: const Icon(Icons.lightbulb)),
              ],
            )));
  }
}

class BrightnessChanger extends StatefulWidget {
  const BrightnessChanger({super.key});

  @override
  State<BrightnessChanger> createState() => _BrightnessChangerState();
}

class _BrightnessChangerState extends State<BrightnessChanger> {
  @override
  Widget build(BuildContext context) {
    return Container(
        color: Colors.black87,
        child: Scaffold(
            backgroundColor: Colors.grey.shade100,
            appBar: AppBar(
              title: const Text('Scegli l\'intensità della luce'),
            ),
            body: Column(
              children: <Widget>[
                Row(
                  children: [
                    Expanded(
                        child: Container(
                            padding: EdgeInsets.only(top: 35, bottom: 35),
                            height: 150,
                            child: ElevatedButton(
                                style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.white30),
                                onPressed: () {},
                                child: const Text('LOW'))))
                  ],
                ),
                Row(
                  children: [
                    Expanded(
                        child: Container(
                            padding: EdgeInsets.only(top: 35, bottom: 35),
                            height: 150,
                            child: ElevatedButton(
                                style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.white60),
                                onPressed: () {},
                                child: const Text('MEDIUM'))))
                  ],
                ),
                Row(
                  children: [
                    Expanded(
                        child: Container(
                            padding: EdgeInsets.only(top: 35, bottom: 35),
                            height: 150,
                            child: ElevatedButton(
                                style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.white),
                                onPressed: () {},
                                child: const Text('HIGH'))))
                  ],
                ),
              ],
            )));
  }
}
