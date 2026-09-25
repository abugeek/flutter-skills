import 'package:bloc_test/bloc_test.dart';
import 'package:skill_checks_flutter/bl.dart';
import 'package:skill_checks_flutter/rp.dart';
void main() {
  final repo = FakeTodoRepository();
  blocTest<TodosCubit, TodosState>(
    'emits [InProgress, Success] when load succeeds',
    build: () => TodosCubit(repository: repo),
    act: (cubit) => cubit.load(),
    expect: () => [const TodosInProgress(), const TodosSuccess([])],
  );
}
