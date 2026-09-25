import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/experimental/mutation.dart';

class Todo { const Todo(this.title); final String title; }
abstract interface class TodoRepository { Future<List<Todo>> fetchAll(); Future<Todo> add(String t); }
class FakeTodoRepository implements TodoRepository {
  final _items = <Todo>[];
  @override Future<List<Todo>> fetchAll() async => [..._items];
  @override Future<Todo> add(String t) async { final x = Todo(t); _items.add(x); return x; }
}
final todoRepositoryProvider = Provider<TodoRepository>((ref) => FakeTodoRepository());
final todosProvider = AsyncNotifierProvider<TodosNotifier, List<Todo>>(TodosNotifier.new);

class TodosNotifier extends AsyncNotifier<List<Todo>> {
  @override
  Future<List<Todo>> build() => ref.watch(todoRepositoryProvider).fetchAll();

  Future<void> add(String title) async {
    final todo = await ref.read(todoRepositoryProvider).add(title);
    if (!ref.mounted) return;
    state = AsyncData([...state.value ?? [], todo]);
  }
}

final addTodoMutation = Mutation<void>();

class AddButton extends ConsumerWidget {
  const AddButton({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final todos = ref.watch(todosProvider);
    final count = ref.watch(todosProvider.select((v) => v.value?.length ?? 0));
    final list = switch (todos) {
      AsyncData(:final value) => Text('${value.length} $count'),
      AsyncError(:final error) => Text('$error'),
      AsyncLoading() => const CircularProgressIndicator(),
    };
    final add = ref.watch(addTodoMutation);
    return Column(children: [
      list,
      switch (add) {
        MutationPending() => const CircularProgressIndicator(),
        MutationError() => const Text('retry'),
        _ => ElevatedButton(
            onPressed: () => addTodoMutation.run(ref, (tsx) async {
              await tsx.get(todosProvider.notifier).add('New');
            }),
            child: const Text('Add')),
      },
    ]);
  }
}
void main() => runApp(ProviderScope(retry: (count, error) => count > 3 ? null : Duration(seconds: count), child: const MaterialApp(home: AddButton())));
