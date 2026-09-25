import 'package:flutter/material.dart';
class const Greeting({super.key, required final String name}) extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Padding(padding: const .all(16), child: Text('Hi $name'));
}
Widget use() => const Greeting(name: 'x');
