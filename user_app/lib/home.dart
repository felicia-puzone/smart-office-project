import 'package:flutter/material.dart';

class UserHome extends StatefulWidget {
  const UserHome({Key? key}) : super(key: key);

  @override
  _UserHomeState createState() => _UserHomeState();
}

class _UserHomeState extends State<UserHome> {
  /* @override
  void dispose() {
    // Clean up the controller when the widget is disposed.
    super.dispose();
  } */

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("HOME"),
      
      ),
      body: Column(
        children: [
          ClipRRect(
                  borderRadius: BorderRadius.circular(50),
                  child: Image(
                    image: NetworkImage(
                        'https://cdn-icons-png.flaticon.com/512/5087/5087579.png'),
                  ),
                ),
        
        ]
      )
    );
  }
}
