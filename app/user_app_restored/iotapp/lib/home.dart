import 'package:flutter/material.dart';
<<<<<<< HEAD
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

final MqttServerClient client =
    MqttServerClient('broker.hivemq.com', 'iot-app');

Future<int> mqttConnect() async {
  /// Set logging on if needed, defaults to off
  client.logging(on: true);

  /// If you intend to use a keep alive you must set it here otherwise keep alive will be disabled.
  client.keepAlivePeriod = 20;

  /// The connection timeout period can be set if needed, the default is 5 seconds.
  client.connectTimeoutPeriod = 2000; // milliseconds

  /// Add the unsolicited disconnection callback
  //Aclient.onDisconnected = onDisconnected;

  /// Add the successful connection callback
  client.onConnected = onConnected;

  /// Add a subscribed callback, there is also an unsubscribed callback if you need it.
  /// You can add these before connection or change them dynamically after connection if
  /// you wish. There is also an onSubscribeFail callback for failed subscriptions, these
  /// can fail either because you have tried to subscribe to an invalid topic or the broker
  /// rejects the subscribe request.
  client.onSubscribed = onSubscribed;

  /// Create a connection message to use or use the default one. The default one sets the
  /// client identifier, any supplied username/password and clean session,
  /// an example of a specific one below.
  final connMess = MqttConnectMessage()
      .withClientIdentifier('Mqtt_MyClientUniqueId')
      .withWillTopic('willtopic') // If you set this you must set a will message
      .withWillMessage('My Will message')
      .startClean() // Non persistent session for testing
      .withWillQos(MqttQos.atLeastOnce);
  print('EXAMPLE::Mosquitto client connecting....');
  client.connectionMessage = connMess;

  /// Connect the client, any errors here are communicated by raising of the appropriate exception. Note
  /// in some circumstances the broker will just disconnect us, see the spec about this, we however will
  /// never send malformed messages.
  try {
    await client.connect();
  } on NoConnectionException catch (e) {
    // Raised by the client when connection fails.
    print('EXAMPLE::client exception - $e');
    client.disconnect();
  } on SocketException catch (e) {
    // Raised by the socket layer
    print('EXAMPLE::socket exception - $e');
    client.disconnect();
  }

  /// Check we are connected
  if (client.connectionStatus!.state == MqttConnectionState.connected) {
    print('EXAMPLE::Mosquitto client connected');
  } else {
    /// Use status here rather than state if you also want the broker return code.
    print(
        'EXAMPLE::ERROR Mosquitto client connection failed - disconnecting, status is ${client.connectionStatus}');
    client.disconnect();
    exit(-1);
  }

  /// Ok, lets try a subscription
  print('EXAMPLE::Subscribing to the test/lol topic');

  String id_edificio = GlobalValues.userSession!.id_edificio.toString();
  String id_room = GlobalValues.userSession!.id_room.toString();

  String topicLightSensor =
      'smartoffice/building_$id_edificio/room_$id_room/sensors/light_sensor'; // Not a wildcard topic
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

    /// The above may seem a little convoluted for users only interested in the
    /// payload, some users however may be interested in the received publish message,
    /// lets not constrain ourselves yet until the package has been in the wild
    /// for a while.
    /// The payload is a byte buffer, this will be specific to the topic
    print(
        'EXAMPLE::Change notification:: topic is <${c[0].topic}>, payload is <-- $lightSensorValue -->');
    print('');
  });

  /// If needed you can listen for published messages that have completed the publishing
  /// handshake which is Qos dependant. Any message received on this stream has completed its
  /// publishing handshake with the broker.
  //client.published!.listen((MqttPublishMessage message) {
  //  print(
  //      'EXAMPLE::Published notification:: topic is ${message.variableHeader!.topicName}, with Qos ${message.header!.qos}');
  //});

  /// Lets publish to our topic
  /// Use the payload builder rather than a raw buffer
  /// Our known topic to publish to

  /// Ok, we will now sleep a while, in this gap you will see ping request/response
  /// messages being exchanged by the keep alive mechanism.
  //print('EXAMPLE::Sleeping....');
  //await MqttUtilities.asyncSleep(60);

  /// Finally, unsubscribe and exit gracefully
  //print('EXAMPLE::Unsubscribing');
  //client.unsubscribe(topic);

  /// Wait for the unsubscribe message from the broker if you wish.
  //await MqttUtilities.asyncSleep(2);
  //print('EXAMPLE::Disconnecting');
  //client.disconnect();
  //print('EXAMPLE::Exiting normally');
  return 0;
=======
import 'userSession.dart';
import 'login.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_emoji/flutter_emoji.dart';

class GlobalValues {
  static UserSession? userSession;
}

Future<UserSession?> fetchUserSession() async {
  String user = userTextController.text;
  String pwd = pwdTextController.text;

  final response = await http.post(
    Uri.parse('http://155.185.74.161:5000/login'),
    headers: <String, String>{
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-ID': 'LOGIN-APP'
    },
    body: ('username=$user&password=$pwd'),
  );

  if (response.statusCode == 200) {
    // If the server did return a 200 OK response,
    // then parse the JSON.
    GlobalValues.userSession = UserSession.fromJson(jsonDecode(response.body));

    return GlobalValues.userSession;
  } else {
    // If the server did not return a 200 OK response,
    // then throw an exception.
    throw Exception('Failed to load UserSession');
  }
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
}

class UserHome extends StatefulWidget {
  const UserHome({super.key});

  @override
  State<UserHome> createState() => _UserHomeState();
}

class _UserHomeState extends State<UserHome> {
  late Future<UserSession?> futureUserSession;
<<<<<<< HEAD
  late Future<int> mqttObject;
  late Future<String> freeRoomFuture;
=======
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd

  @override
  void initState() {
    super.initState();

<<<<<<< HEAD
    try {
      mqttConnect();
    } catch (e) {
      print('Errore connessione MQTT: $e');
    }
=======
    futureUserSession = fetchUserSession();
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
<<<<<<< HEAD
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
                                  Icon(Icons.sunny),
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
                                    style: const TextStyle(
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
                                  style: const TextStyle(
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
                                Text(
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
                                      Text(
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
                                                style: TextStyle(
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
                                      Text(
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
                                                style: TextStyle(
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

//////// MQTT ROBA //////////////////////////////

void onSubscribed(String topic) {
  print('EXAMPLE::Subscription confirmed for topic $topic');
}

/// The unsolicited disconnect callback
void onDisconnected() {
  print('EXAMPLE::OnDisconnected client callback - Client disconnection');
  if (client.connectionStatus!.disconnectionOrigin ==
      MqttDisconnectionOrigin.solicited) {
    print('EXAMPLE::OnDisconnected callback is solicited, this is correct');
  } else {
    print(
        'EXAMPLE::OnDisconnected callback is unsolicited or none, this is incorrect - exiting');
    exit(-1);
  }
}

/// The successful connect callback
void onConnected() {
  print(
      'EXAMPLE::OnConnected client callback - Client connection was successful');
}
=======
            body:
                 FutureBuilder<UserSession?>(
                  future: futureUserSession,
                  builder: (context, snapshot) {
                    if (snapshot.hasData) {
                      if (snapshot.data!.logged_in == true) {
                        return Center(
                                child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      const SizedBox(
                                      height: 90,
                                    ),
                              Container(
                                  margin: const EdgeInsets.only(
                                      left: 35, right: 35),
                                  child: Column(children: [
                                    Container(
                                        child: Text(
                                          'Benvenuto ' +
                                              GlobalValues.userSession!.username
                                                  .toString() +
                                              '! 🖖',
                                          style: const TextStyle(
                                              color: Colors.black,
                                              fontSize: 27),
                                        ),
                                        decoration: BoxDecoration(
                                            color: Colors.grey.shade100,
                                            borderRadius:
                                                BorderRadius.circular(5)),
                                        padding: const EdgeInsets.all(8.0)),
                                    const SizedBox(
                                      height: 30,
                                    )
                                  ]))
                            ]));
                      }

                      ////////////////////////
                      ///////////////////////

                      else if (snapshot.data!.logged_in == false) {
                        return AlertDialog(
                          title: const Text('Login Fallito'),
                          alignment: Alignment.center,
                          actions: <Widget>[
                            TextButton(
                              onPressed: () => Navigator.pop(context, 'OK'),
                              child: const Text('OK'),
                            ),
                          ],
                        );
                      }
                    } else if (snapshot.hasError) {
                      return Text('${snapshot.error}');
                    }

                    // By default, show a loading spinner.
                    return const CircularProgressIndicator();
                  },
                ),
              )
            );
  }
}
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
