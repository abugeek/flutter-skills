import 'package:equatable/equatable.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'rp.dart' show Todo, TodoRepository;

sealed class TodosState extends Equatable { const TodosState(); @override List<Object?> get props => []; }
final class TodosInitial extends TodosState { const TodosInitial(); }
final class TodosInProgress extends TodosState { const TodosInProgress(); }
final class TodosSuccess extends TodosState { const TodosSuccess(this.todos); final List<Todo> todos; @override List<Object?> get props => [todos]; }
final class TodosFailure extends TodosState { const TodosFailure(this.error); final Object error; @override List<Object?> get props => [error]; }

class TodosCubit extends Cubit<TodosState> {
  TodosCubit({required TodoRepository repository}) : _repository = repository, super(const TodosInitial());
  final TodoRepository _repository;

  Future<void> load() async {
    emit(const TodosInProgress());
    try {
      final todos = await _repository.fetchAll();
      if (isClosed) return;
      emit(TodosSuccess(todos));
    } catch (e, s) {
      addError(e, s);
      if (!isClosed) emit(TodosFailure(e));
    }
  }
}

class TodosPage extends StatelessWidget {
  const TodosPage({super.key});
  @override
  Widget build(BuildContext context) => BlocProvider(
        create: (context) => TodosCubit(repository: context.read<TodoRepository>())..load(),
        child: const TodosView(),
      );
}
class TodosView extends StatelessWidget {
  @visibleForTesting
  const TodosView({super.key});
  @override
  Widget build(BuildContext context) => switch (context.watch<TodosCubit>().state) {
        TodosInitial() || TodosInProgress() => const Center(child: CircularProgressIndicator()),
        TodosSuccess(:final todos) => Text('${todos.length}'),
        TodosFailure() => const Text('error'),
      };
}
