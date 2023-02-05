import 'package:flutter/material.dart';
import 'package:iotapp/login.dart';
import 'models.dart';
import 'controller.dart';
import 'rooms_map.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import 'dart:async';
import 'dart:io';
import 'change_values.dart';

ValueNotifier<String> lightSensorValue = ValueNotifier<String>('0');
ValueNotifier<String> noiseSensorValue = ValueNotifier<String>('0');

void onSubscribed(String topic) {
  print('MQTT::Subscription confirmed for topic $topic');
}

void onDisconnected() {
  print('MQTT::OnDisconnected client callback - Client disconnection');
  if (client.connectionStatus!.disconnectionOrigin ==
      MqttDisconnectionOrigin.solicited) {
    print('MQTT::OnDisconnected callback is solicited, this is correct');
  } else {
    print(
        'MQTT::OnDisconnected callback is unsolicited or none, this is incorrect - exiting');
  }
}

void onConnected() {
  print('MQTT::OnConnected client callback - Client connection was successful');
}

final MqttServerClient client =
    MqttServerClient('broker.hivemq.com', 'iot-app');

Future<int> mqttConnect() async {
  client.logging(on: true);
  client.keepAlivePeriod = 20;
  client.connectTimeoutPeriod = 4000; // milliseconds
  client.onDisconnected = onDisconnected;
  client.onConnected = onConnected;
  client.onSubscribed = onSubscribed;

  final connMess = MqttConnectMessage()
      .withClientIdentifier('app_unique_id')
      .withWillTopic(
          'appWillTopic') // If you set this you must set a will message
      .withWillMessage('App disconnected')
      .startClean() // Non persistent session for testing
      .withWillQos(MqttQos.atLeastOnce);
  print('MQTT::Client connecting....');
  client.connectionMessage = connMess;

  try {
    await client.connect();
  } on NoConnectionException catch (e) {
    // Raised by the client when connection fails.
    print('MQTT::client exception - $e');
    client.disconnect();
  } on SocketException catch (e) {
    // Raised by the socket layer
    print('MQTT::socket exception - $e');
    client.disconnect();
  }

  /// Check we are connected
  if (client.connectionStatus!.state == MqttConnectionState.connected) {
    print('MQTT::Client connected');
  } else {
    print(
        'MQTT::Client connection failed - disconnecting, status is ${client.connectionStatus}');
    client.disconnect();
  }

  String id_edificio = GlobalValues.userSession!.id_edificio.toString();
  String id_room = GlobalValues.userSession!.id_room.toString();

  String topicLightSensor =
      'smartoffice/building_$id_edificio/room_$id_room/sensors/light_sensor';
  String topicNoiseSensor =
      'smartoffice/building_$id_edificio/room_$id_room/sensors/noise_sensor';
  client.subscribe(topicLightSensor, MqttQos.atMostOnce);
  client.subscribe(topicNoiseSensor, MqttQos.atMostOnce);

  /// The client has a change notifier object(see the Observable class) which we then listen to to get
  /// notifications of published updates to each subscribed topic.
  client.updates!.listen((List<MqttReceivedMessage<MqttMessage?>>? c) {
    final recMess = c![0].payload as MqttPublishMessage;

    if (c[0].topic == topicNoiseSensor) if (MqttPublishPayload
            .bytesToStringAsString(recMess.payload.message) ==
        '1')
      noiseSensorValue.value = 'ALTO';
    else
      noiseSensorValue.value = 'NORMALE';
    if (c[0].topic == topicLightSensor)
      lightSensorValue.value =
          MqttPublishPayload.bytesToStringAsString(recMess.payload.message);

    print(
        'MQTT::Change notification:: topic is <${c[0].topic}>, payload is <-- $lightSensorValue -->'
        'MQTT::Change notification:: topic is <${c[0].topic}>, payload is <-- $noiseSensorValue -->');
  });
  return 0;
}

class UserHome extends StatefulWidget {
  const UserHome({super.key});

  @override
  State<UserHome> createState() => _UserHomeState();
}

class _UserHomeState extends State<UserHome> {
  late Future<UserSession?> futureUserSession;
  late Future<int> mqttObject;
  late Future<String> freeRoomFuture;

  @override
  void initState() {
    super.initState();

    try {
      mqttConnect();
    } catch (e) {
      print('Errore connessione MQTT: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
        decoration: BoxDecoration(
          image: DecorationImage(
              image: AssetImage('assets/register.png'), fit: BoxFit.cover),
        ),
        child: Scaffold(
            backgroundColor: Colors.transparent,
            body: Container(
                child: SingleChildScrollView(
                    child: Center(
                        child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                  const SizedBox(
                    height: 90,
                  ),
                  Container(
                    margin: const EdgeInsets.only(left: 35, right: 35),
                    child: Column(children: [
                      Container(
                          child: Text(
                            'Benvenuto ' +
                                GlobalValues.userSession!.username.toString() +
                                '! 🖖',
                            style: const TextStyle(
                                color: Colors.black, fontSize: 27),
                          ),
                          decoration: BoxDecoration(
                              color: Colors.grey.shade100,
                              borderRadius: BorderRadius.circular(5)),
                          padding: const EdgeInsets.all(8.0)),

                      const SizedBox(
                        height: 30,
                      ),

                      Image.asset('assets/profile_picture.png'),
                      const SizedBox(
                        height: 30,
                      ),

                      //METEO E LUOGO

                      Container(
                          padding: const EdgeInsets.all(10.0),
                          decoration: BoxDecoration(
                              color: Colors.orange,
                              borderRadius: BorderRadius.circular(5)),
                          child: Column(children: [
                            Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    'Meteo',
                                    style: TextStyle(
                                        fontSize: 20,
                                        fontWeight: FontWeight.w700),
                                  ),
                                  const Icon(Icons.sunny),
                                ]),
                            const SizedBox(
                              height: 15,
                            ),
                            Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  const Text(
                                    'Temperatura esterna',
                                    style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.w700),
                                  ),
                                  Text(
                                    GlobalValues.weatherInfo.ext_temp + '°',
                                    style: const TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.w700),
                                  )
                                ]),
                            const SizedBox(
                              height: 10,
                            ),
                            Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  const Text(
                                    'Umidità esterna',
                                    style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.w700),
                                  ),
                                  Text(
                                    GlobalValues.weatherInfo.ext_humidity,
                                    style: const TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.w700),
                                  )
                                ]),
                            const Divider(
                              height: 20,
                              thickness: 2,
                              color: Colors.black,
                            ),
                            Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  const Text(
                                    'Luogo',
                                    style: TextStyle(
                                        fontSize: 20,
                                        fontWeight: FontWeight.w700),
                                  ),
                                  const Icon(Icons.pin_drop_sharp),
                                  Text(
                                    GlobalValues.weatherInfo.city_name,
                                    style: const TextStyle(
                                        fontSize: 20,
                                        fontWeight: FontWeight.w700),
                                  )
                                ])
                          ])),

                      const SizedBox(
                        height: 55,
                      ),
                      //Sensore luce
                      Container(
                          padding: const EdgeInsets.all(10.0),
                          decoration: BoxDecoration(
                              color: Colors.grey.shade100,
                              borderRadius: BorderRadius.circular(5)),
                          child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text(
                                  'Luminosità rilevata',
                                  style: TextStyle(
                                      fontSize: 20,
                                      fontWeight: FontWeight.w700),
                                ),
                                ValueListenableBuilder(
                                  valueListenable: lightSensorValue,
                                  builder: (context, value, child) {
                                    return Text(value.toString(),
                                        style: const TextStyle(
                                            fontSize: 20,
                                            fontWeight: FontWeight.w700));
                                  },
                                ),
                              ])),

                      const SizedBox(
                        height: 30,
                      ),

                      //Umidità
                      Container(
                          padding: const EdgeInsets.all(10.0),
                          decoration: BoxDecoration(
                              color: Colors.grey.shade100,
                              borderRadius: BorderRadius.circular(5)),
                          child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text(
                                  'Rumore rilevato',
                                  style: TextStyle(
                                      fontSize: 20,
                                      fontWeight: FontWeight.w700),
                                ),
                                ValueListenableBuilder(
                                  valueListenable: noiseSensorValue,
                                  builder: (context, value, child) {
                                    return Text(value.toString(),
                                        style: const TextStyle(
                                            fontSize: 20,
                                            fontWeight: FontWeight.w700));
                                  },
                                ),
                              ])),

                      const SizedBox(
                        height: 30,
                      ),

                      //Led
                      Container(
                        padding: const EdgeInsets.all(10.0),
                        decoration: BoxDecoration(
                            color: Colors.grey.shade100,
                            borderRadius: BorderRadius.circular(5)),
                        child: Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                  children: [
                                    const Text(
                                      'Colore luce',
                                      style: TextStyle(
                                          fontSize: 20,
                                          fontWeight: FontWeight.w700),
                                    ),
                                    ValueListenableBuilder(
                                      valueListenable: digitalTwinValue,
                                      builder: (context, value, child) {
                                        return Text(
                                            digitalTwinValue.value.room_color
                                                .toString(),
                                            style: const TextStyle(
                                                fontSize: 20,
                                                fontWeight: FontWeight.w700));
                                      },
                                    ),
                                  ]),
                              const SizedBox(
                                height: 5,
                              ),
                              ElevatedButton(
                                  style: ElevatedButton.styleFrom(
                                      textStyle: const TextStyle(
                                        color: Color(0xff4c505b),
                                        fontSize: 20,
                                      ),
                                      backgroundColor: Colors.orangeAccent),
                                  onPressed: () {
                                    Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                            builder: (context) =>
                                                ColorChanger(client: client)));
                                  },
                                  child: const Icon(Icons.edit))
                            ]),
                      ),

                      const SizedBox(
                        height: 30,
                      ),

                      //LED intensity
                      Container(
                          padding: const EdgeInsets.all(10.0),
                          decoration: BoxDecoration(
                              color: Colors.grey.shade100,
                              borderRadius: BorderRadius.circular(5)),
                          child: Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      const Text(
                                        'Intensità luce',
                                        style: TextStyle(
                                            fontSize: 20,
                                            fontWeight: FontWeight.w700),
                                      ),
                                      ValueListenableBuilder(
                                          valueListenable: digitalTwinValue,
                                          builder: (context, value, child) {
                                            return Text(
                                                digitalTwinValue
                                                    .value.room_brightness
                                                    .toString(),
                                                style: const TextStyle(
                                                    fontSize: 20,
                                                    fontWeight:
                                                        FontWeight.w700));
                                          }),
                                    ]),
                                const SizedBox(
                                  height: 5,
                                ),
                                ElevatedButton(
                                    style: ElevatedButton.styleFrom(
                                        textStyle: const TextStyle(
                                          color: Color(0xff4c505b),
                                          fontSize: 20,
                                        ),
                                        backgroundColor: Colors.orangeAccent),
                                    onPressed: () {
                                      Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                              builder: (context) =>
                                                  BrightnessChanger()));
                                    },
                                    child: const Icon(Icons.edit))
                              ])),

                      const SizedBox(
                        height: 30,
                      ),

                      //Temperatura
                      Container(
                          padding: const EdgeInsets.all(10.0),
                          decoration: BoxDecoration(
                              color: Colors.grey.shade100,
                              borderRadius: BorderRadius.circular(5)),
                          child: Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      const Text(
                                        'Temperatura',
                                        style: TextStyle(
                                            fontSize: 20,
                                            fontWeight: FontWeight.w700),
                                      ),
                                      ValueListenableBuilder(
                                          valueListenable: digitalTwinValue,
                                          builder: (context, value, child) {
                                            return Text(
                                                digitalTwinValue
                                                    .value.room_temperature
                                                    .toString(),
                                                style: const TextStyle(
                                                    fontSize: 20,
                                                    fontWeight:
                                                        FontWeight.w700));
                                          }),
                                    ]),
                                const SizedBox(
                                  height: 5,
                                ),
                                ElevatedButton(
                                    style: ElevatedButton.styleFrom(
                                        textStyle: const TextStyle(
                                          color: Color(0xff4c505b),
                                          fontSize: 20,
                                        ),
                                        backgroundColor: Colors.orangeAccent),
                                    onPressed: () {
                                      Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                              builder: (context) =>
                                                  TemperatureChanger()));
                                    },
                                    child: const Icon(Icons.edit))
                              ])),

                      Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Expanded(
                                child: Container(
                              padding:
                                  const EdgeInsets.only(top: 35, bottom: 35),
                              height: 150,
                              child: ElevatedButton(
                                  style: ElevatedButton.styleFrom(
                                      textStyle: const TextStyle(
                                        color: Color(0xff4c505b),
                                        fontSize: 20,
                                      ),
                                      backgroundColor: Colors.orangeAccent),
                                  onPressed: () async {
                                    final response = await freeRoom();

                                    if (response == 'REQUEST-OK')
                                      Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                              builder: (context) => Mappa()));
                                  },
                                  child: const Text('LASCIA STANZA')),
                            ))
                          ]),
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
                                  onPressed: () async {
                                    logout();

                                    Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                            builder: (context) => MyLogin()));
                                  },
                                  child: const Text('LOGOUT')),
                            ))
                          ])
                    ]),
                  ),
                ]))))));
  }
}
