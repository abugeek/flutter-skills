import 'package:flutter/material.dart';
import 'package:patrol/patrol.dart';

void main() {
  patrolTest('user grants location permission', ($) async {
    await $.pumpWidgetAndSettle(const MaterialApp(home: Text('x')));
    await $.platform.mobile.grantPermissionWhenInUse();
    await $(TextField).enterText('Patrol');
    await $(ListTile).containing('Part 1').$(Icons.arrow_forward).scrollTo().tap();
    await $(ElevatedButton).at(2).tap();
  });
}
