// Snippets from flutter-dart-style SKILL.md, compiled as-is.
class Point(final int x, final int y);
class const Money(final int cents, final String currency);
class User({required final String _id, final String? nickname}) {
  String get id => _id;
}
class Person(final String name);
class Admin(super.name, final Set<String> roles) extends Person;
class Temp(final double celsius) {
  this : assert(celsius > -273.15);
}
class P2 {
  double x, y;
  new(this.x, this.y);
  new origin() : x = 0, y = 0;
  factory clone(P2 o) => P2(o.x, o.y);
}
class PrivNamed {
  final int _x;
  PrivNamed({required this._x});
  int get x => _x;
}

sealed class Shape {}
final class Circle(final double r) extends Shape;
final class Square(final double side) extends Shape;
double area(Shape s) => switch (s) { Circle(:final r) => 3.14159 * r * r, Square(:final side) => side * side };

extension type UserId(String value) {}
extension type Json(Map<String, Object?> m) { String get name => m['name'] as String; }

enum Status { none, running }

sealed class Result<T> {
  const Result();
  const factory Result.ok(T value) = Ok._;
  const factory Result.error(Exception error) = Error._;
}
final class Ok<T> extends Result<T> { const Ok._(this.value); final T value; }
final class Error<T> extends Result<T> { const Error._(this.error); final Exception error; }

Future<(String, int)> login() async => ('u', 1);
Future<int> fa() async => 1;
Future<String> fb() async => 'b';

Future<void> demo(Object? x, Map<String, Object?> json, String? maybeBanner, List<String>? extra, bool isAdmin) async {
  if (x case final String v?) print(v);
  if (json case {'name': String name, 'age': int age}) print('$name $age');
  Status s = .running;
  final list = ['header', ?maybeBanner, if (isAdmin) 'admin', for (final i in [1, 2]) '$i', ...?extra];
  final (a, b) = await (fa(), fb()).wait;
  final (user, token) = await login();
  final u = User(id: 'x');
  final p = PrivNamed(x: 1);
  print([s, list, a, b, user, token, u.id, p.x, Point(1, 2).x, const Money(1, 'USD'), Admin('n', {}).roles, P2.origin().x, Temp(1).celsius, UserId('1').value, Json({'name': 'n'}).name]);
  final r = const Result<int>.ok(1);
  if (r case Ok(:final value)) print(value);
}
