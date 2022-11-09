/*import 'package:flutter/material.dart';
import 'package:pizzapp/src/widget/carousel.dart';
import 'package:pizzapp/src/classes/pizza.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

Future<Pizza> fetchPizza() async {
  final response =
      await http.get(Uri.parse('https://gorest.co.in/public/v2/users/4427'));

  if (response.statusCode == 200) {
    // If the server did return a 200 OK response,
    // then parse the JSON.
    return Pizza.fromJson(jsonDecode(response.body));
  } else {
    // If the server did not return a 200 OK response,
    // then throw an exception.
    throw Exception('Failed to load pizza');
  }
}

class PizzaResponse extends StatefulWidget {
  const PizzaResponse({super.key});

  @override
  State<PizzaResponse> createState() => _PizzaResponseState();
}

class _PizzaResponseState extends State<PizzaResponse> {
  late Future<Pizza> futurePizza;

  @override
  void initState() {
    super.initState();
    futurePizza = fetchPizza();
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: FutureBuilder<Pizza>(
        future: futurePizza,
        builder: (context, snapshot) {
          if (snapshot.hasData) {
            return Text(snapshot.data!.name +
                ' ' +
                snapshot.data!.email +
                ' ' +
                snapshot.data!.gender);
          } else if (snapshot.hasError) {
            return Text('${snapshot.error}');
          }

          // By default, show a loading spinner.
          return const CircularProgressIndicator();
        },
      ),
    );
  }
}

class RestSenderDemo extends StatelessWidget {
  const RestSenderDemo({super.key});

  @override
  Widget build(BuildContext context) {
    final ButtonStyle style =
        ElevatedButton.styleFrom(textStyle: const TextStyle(fontSize: 20));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Fetch Data Example'),
      ),
      body: Center(
        child: Column(
          children: <Widget>[
            const Text("Fetch user from URL"),
            ElevatedButton(
              style: style,
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => PizzaResponse()),
                );
              },
              child: const Text('GET'),
            ),
          ],
        ),
      ),
    );
  }
}
*/