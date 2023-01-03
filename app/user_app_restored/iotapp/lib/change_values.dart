import 'package:flutter/material.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';

import 'package:http/http.dart' as http;
import 'dart:async';
import 'dart:convert';

class UpdateReq {
  final String id_utente;
  final String color_val;
  final String brightness_val;
  final String temp_val;

  UpdateReq(this.id_utente, this.color_val, this.brightness_val, this.temp_val);

  UpdateReq.fromJson(Map<String, dynamic> json)
      : id_utente = json['id_utente'],
        color_val = json['color_val'],
        brightness_val = json['brightness_val'],
        temp_val = json['temp_val'];

  Map<String, dynamic> toJson() => {
        'id_utente': id_utente,
        'color_val': color_val,
        'brightness_val': brightness_val,
        'temp_val': temp_val
      };
}

//TEMPORANEA
Future<String?> UpdateRoom(UpdateReq request) async {
  final response = await http.post(
    Uri.parse('http://192.168.1.240:5000/update'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'UPDATE-APP'
    },
    body: jsonEncode(request.toJson()),
  );

  if (response.statusCode == 200) {
    // If the server did return a 200 OK response,
    // then parse the JSON.

  } else {
    // If the server did not return a 200 OK response,
    // then throw an exception.
    throw Exception('Failed to send UPDATE');
  }
}

Future<String?> changeActuatorRequest(UpdateReq request) async {
  final response = await http.post(
    Uri.parse('http://192.168.1.240:5000/update'),
    headers: <String, String>{
      'Content-Type': 'application/json',
      'Content-ID': 'UPDATE-APP'
    },
    body: jsonEncode(request.toJson()),
  );

  if (response.statusCode == 200) {
    // If the server did return a 200 OK response,
    // then parse the JSON.

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
                          'idddd', 'color_val', 'brightness_val', 'temppp'));
                    },
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.yellow),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style:
                        ElevatedButton.styleFrom(backgroundColor: Colors.green),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.tealAccent),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.lightBlue),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.indigo),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style:
                        ElevatedButton.styleFrom(backgroundColor: Colors.pink),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style:
                        ElevatedButton.styleFrom(backgroundColor: Colors.grey),
                    onPressed: () {},
                    child: const Icon(Icons.lightbulb)),
              ],
            )));
  }
}



/*
class ColorChanger extends StatelessWidget {
  const ColorChanger({super.key});

  final Color borderColor;

  const ColorChanger(this.borderColor);

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
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.yellow),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style:
                        ElevatedButton.styleFrom(backgroundColor: Colors.green),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.tealAccent),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.lightBlue),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.indigo),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style:
                        ElevatedButton.styleFrom(backgroundColor: Colors.pink),
                    onPressed: () {},
                    child: const Text(' ')),
                ElevatedButton(
                    style:
                        ElevatedButton.styleFrom(backgroundColor: Colors.grey),
                    onPressed: () {},
                    child: const Icon(Icons.lightbulb)),
              ],
            )));
  }
}
*/
