import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:skill_checks_flutter/rp.dart';
void main() {
  test('adds todo', () async {
    final container = ProviderContainer.test(overrides: [
      todoRepositoryProvider.overrideWithValue(FakeTodoRepository()),
    ]);
    await container.read(todosProvider.future);
    await container.read(todosProvider.notifier).add('x');
    expect(container.read(todosProvider).value, hasLength(1));
  });
}
