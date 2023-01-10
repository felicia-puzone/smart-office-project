import 'package:flutter/material.dart';
import 'package:iotapp/controller.dart';
import 'login.dart';
import 'models.dart';
import 'package:intl/intl.dart';

List<String> sexList = ['Maschio', 'Femmina', 'Altro'];
List<Profession> professionList = [];

class MyRegister extends StatefulWidget {
  MyRegister({Key? key}) : super(key: key);

  @override
  _MyRegisterState createState() => _MyRegisterState();
}

class _MyRegisterState extends State<MyRegister> {
  final Future<List<Profession>> _listProfessions = fetchJobs();
  TextEditingController dateInput = TextEditingController();
  String choosenProfession = '';
  String sex = sexList.first;

  String _dropdownValueProfession = '';
  String _dropdownValueSex = sexList.first;

  final _userTextController = TextEditingController();
  final _pwdTextController = TextEditingController();
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        image: DecorationImage(
            image: AssetImage('assets/register.png'), fit: BoxFit.cover),
      ),
      child: Scaffold(
          backgroundColor: Colors.transparent,
          appBar: AppBar(
            backgroundColor: Colors.transparent,
            elevation: 0,
          ),
          body: FutureBuilder<List<Profession>>(
              future:
                  _listProfessions, // a previously-obtained Future<String> or null
              builder: (BuildContext context,
                  AsyncSnapshot<List<Profession>> snapshot) {
                if (snapshot.hasData) {
                  professionList = snapshot.data!;
                  _dropdownValueProfession = professionList.first.name;
                  choosenProfession = professionList.first.name;

                  return Stack(
                    children: [
                      Container(
                        padding: EdgeInsets.only(left: 35, top: 30),
                        child: Text(
                          'Crea\nAccount',
                          style: TextStyle(color: Colors.white, fontSize: 33),
                        ),
                      ),
                      SingleChildScrollView(
                        child: Container(
                          padding: EdgeInsets.only(
                              top: MediaQuery.of(context).size.height * 0.28),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                margin: EdgeInsets.only(left: 35, right: 35),
                                child: Column(
                                  children: [
                                    TextField(
                                      controller: _userTextController,
                                      style: TextStyle(color: Colors.white),
                                      decoration: InputDecoration(
                                          enabledBorder: OutlineInputBorder(
                                            borderRadius:
                                                BorderRadius.circular(10),
                                            borderSide: BorderSide(
                                              color: Colors.white,
                                            ),
                                          ),
                                          focusedBorder: OutlineInputBorder(
                                            borderRadius:
                                                BorderRadius.circular(10),
                                            borderSide: BorderSide(
                                              color: Colors.black,
                                            ),
                                          ),
                                          hintText: "Username",
                                          hintStyle:
                                              TextStyle(color: Colors.white),
                                          border: OutlineInputBorder(
                                            borderRadius:
                                                BorderRadius.circular(10),
                                          )),
                                    ),
                                    SizedBox(
                                      height: 30,
                                    ),
                                    TextField(
                                      controller: _pwdTextController,
                                      style: TextStyle(color: Colors.white),
                                      decoration: InputDecoration(
                                          enabledBorder: OutlineInputBorder(
                                            borderRadius:
                                                BorderRadius.circular(10),
                                            borderSide: BorderSide(
                                              color: Colors.white,
                                            ),
                                          ),
                                          focusedBorder: OutlineInputBorder(
                                            borderRadius:
                                                BorderRadius.circular(10),
                                            borderSide: BorderSide(
                                              color: Colors.black,
                                            ),
                                          ),
                                          hintText: "Password",
                                          hintStyle:
                                              TextStyle(color: Colors.white),
                                          border: OutlineInputBorder(
                                            borderRadius:
                                                BorderRadius.circular(10),
                                          )),
                                    ),
                                    SizedBox(
                                      height: 30,
                                    ),
                                    Text(
                                      'Professione',
                                      style: TextStyle(fontSize: 14),
                                    ),
                                    DropdownButton<String>(
                                      value: _dropdownValueProfession,
                                      icon: const Icon(Icons.arrow_downward),
                                      elevation: 16,
                                      style: const TextStyle(
                                          color: Colors.black87),
                                      underline: Container(
                                        height: 2,
                                        color: Colors.black54,
                                      ),
                                      onChanged: (String? value) {
                                        // This is called when the user selects an item.
                                        setState(() {
                                          _dropdownValueProfession = value!;
                                          choosenProfession =
                                              _dropdownValueProfession;
                                        });
                                      },
                                      items: (snapshot.data!
                                              .map((element) => element.name)
                                              .toList())
                                          .map<DropdownMenuItem<String>>(
                                              (String value) {
                                        return DropdownMenuItem<String>(
                                          value: value,
                                          child: Text(value),
                                        );
                                      }).toList(),
                                    ),
                                    SizedBox(
                                      height: 40,
                                    ),
                                    Text(
                                      'Sesso',
                                      style: TextStyle(fontSize: 14),
                                    ),
                                    DropdownButton<String>(
                                      value: _dropdownValueSex,
                                      icon: const Icon(Icons.arrow_downward),
                                      elevation: 16,
                                      style: const TextStyle(
                                          color: Colors.black87),
                                      underline: Container(
                                        height: 2,
                                        color: Colors.black54,
                                      ),
                                      onChanged: (String? value) {
                                        // This is called when the user selects an item.
                                        setState(() {
                                          _dropdownValueSex = value!;
                                          sex = _dropdownValueSex;
                                        });
                                      },
                                      items: sexList
                                          .map<DropdownMenuItem<String>>(
                                              (String value) {
                                        return DropdownMenuItem<String>(
                                          value: value,
                                          child: Text(value),
                                        );
                                      }).toList(),
                                    ),
                                    SizedBox(
                                      height: 40,
                                    ),
                                    TextField(
                                      controller: dateInput,
//editing controller of this TextField
                                      decoration: InputDecoration(
                                          icon: Icon(Icons
                                              .calendar_today), //icon of text field
                                          labelText:
                                              "Data di nascita" //label text of field
                                          ),
                                      readOnly: true,
//set it true, so that user will not able to edit text
                                      onTap: () async {
                                        DateTime? pickedDate =
                                            await showDatePicker(
                                                context: context,
                                                initialDate: DateTime.now(),
                                                firstDate: DateTime(1950),
//DateTime.now() - not to allow to choose before today.
                                                lastDate: DateTime(2100));

                                        if (pickedDate != null) {
                                          print(
                                              pickedDate); //pickedDate output format => 2021-03-10 00:00:00.000
                                          String formattedDate =
                                              DateFormat('yyyy-MM-dd')
                                                  .format(pickedDate);
                                          print(
                                              formattedDate); //formatted date output using intl package =>  2021-03-16
                                          setState(() {
                                            dateInput.text = formattedDate;
                                            //set output date to TextField value.
                                          });
                                        } else {}
                                      },
                                    ),
                                    SizedBox(
                                      height: 40,
                                    ),
                                    Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          'Registrazione',
                                          style: TextStyle(
                                              color: Colors.white,
                                              fontSize: 27,
                                              fontWeight: FontWeight.w700),
                                        ),
                                        CircleAvatar(
                                          radius: 30,
                                          backgroundColor: Color(0xff4c505b),
                                          child: IconButton(
                                              color: Colors.white,
                                              onPressed: () async {
                                                int sexId;
                                                if (this.sex == 'Maschio')
                                                  sexId = 0;
                                                if (this.sex == 'Femmina')
                                                  sexId = 1;
                                                else
                                                  sexId = 2;

                                                int professionId = 0;

                                                try {
                                                  professionId = professionList
                                                      .where((obj) =>
                                                          obj.name ==
                                                          choosenProfession)
                                                      .first
                                                      .id;
                                                } catch (e) {}

                                                String result =
                                                    await registerUser(
                                                        this
                                                            ._userTextController
                                                            .text,
                                                        this
                                                            ._pwdTextController
                                                            .text,
                                                        sexId,
                                                        professionId,
                                                        this.dateInput.value);
                                                showDialog(
                                                    context: context,
                                                    builder:
                                                        (ctx) => AlertDialog(
                                                              title:
                                                                  Text(result),
                                                              actions: <Widget>[
                                                                TextButton(
                                                                  onPressed:
                                                                      () {
                                                                    Navigator.pushNamed(
                                                                        context,
                                                                        'login');
                                                                  },
                                                                  child:
                                                                      Container(
                                                                    padding:
                                                                        const EdgeInsets.all(
                                                                            14),
                                                                    child:
                                                                        const Text(
                                                                            "OK"),
                                                                  ),
                                                                ),
                                                              ],
                                                            ));
                                              },
                                              icon: Icon(
                                                Icons.arrow_forward,
                                              )),
                                        )
                                      ],
                                    ),
                                    SizedBox(
                                      height: 40,
                                    ),
                                    Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.spaceBetween,
                                      children: [
                                        TextButton(
                                          onPressed: () {
                                            Navigator.pushNamed(
                                                context, 'login');
                                            // Navigator.of(context).push(_createRoute());
                                          },
                                          child: Text(
                                            'Login',
                                            textAlign: TextAlign.left,
                                            style: TextStyle(
                                                decoration:
                                                    TextDecoration.underline,
                                                color: Colors.white,
                                                fontSize: 18),
                                          ),
                                          style: ButtonStyle(),
                                        ),
                                      ],
                                    )
                                  ],
                                ),
                              )
                            ],
                          ),
                        ),
                      ),
                    ],
                  );
                } else
                  return CircularProgressIndicator();
              })),
    );
  }
}

// Route _createRoute() {
//   return PageRouteBuilder(
//     pageBuilder: (context, animation, secondaryAnimation) => const MyLogin(),
//     transitionsBuilder: (context, animation, secondaryAnimation, child) {
//       return child;
//     },
//   );
// }

class DropDownButtonRegister extends StatefulWidget {
  final List<String> list;

  const DropDownButtonRegister({super.key, required this.list});

  @override
  State<DropDownButtonRegister> createState() => _DropDownButtonRegisterState();
}

class _DropDownButtonRegisterState extends State<DropDownButtonRegister> {
  String _dropdownValue = '';

  @override
  void initState() {
    _dropdownValue = widget.list.first;
  }

  @override
  Widget build(BuildContext context) {
    return DropdownButton<String>(
      value: _dropdownValue,
      icon: const Icon(Icons.arrow_downward),
      elevation: 16,
      style: const TextStyle(color: Colors.black87),
      underline: Container(
        height: 2,
        color: Colors.black54,
      ),
      onChanged: (String? value) {
        // This is called when the user selects an item.
        setState(() {
          _dropdownValue = value!;
        });
      },
      items: widget.list.map<DropdownMenuItem<String>>((String value) {
        return DropdownMenuItem<String>(
          value: value,
          child: Text(value),
        );
      }).toList(),
    );
  }
}
