# Bloc / Cubit (bloc 9.2, flutter_bloc 9.1, bloc_test 10, bloc_concurrency 0.3) — verified 2026-09-25

## Cubit first
Use `Cubit` by default (methods → `emit`). Use `Bloc` (events → states) when you need event transformers (debounce search, drop duplicate taps, restartable requests) or an audit trail of events.

## Naming (bloclibrary.dev conventions, strongly recommended for teams)
- Events are **past tense**: `LoginSubmitted`, `TodoListStarted` (initial load = `Subject` + `Started`). Base class: `LoginEvent`.
- States are **nouns**. Subclasses: `LoginInitial | LoginInProgress | LoginSuccess | LoginFailure`, base class `LoginState`. Single class: `LoginState` + `enum LoginStatus { initial, loading, success, failure }`.

## Modeling state: choose deliberately
| Sealed class + subclasses | Single class + status enum |
|---|---|
| Exclusive states with their own data (`loading` / `ready(items)` / `failure(reason)`) | States that overlap: keep old data while loading more, show an error snackbar while still showing data, multi-step forms |
| Type-safe, exhaustive `switch` | Concise, `copyWith`, but fields are nullable and you must check `status` |

```dart
sealed class TodosState extends Equatable { const TodosState(); @override List<Object?> get props => []; }
final class TodosInitial extends TodosState { const TodosInitial(); }
final class TodosInProgress extends TodosState { const TodosInProgress(); }
final class TodosSuccess extends TodosState { const TodosSuccess(this.todos); final List<Todo> todos; @override List<Object?> get props => [todos]; }
final class TodosFailure extends TodosState { const TodosFailure(this.error); final Object error; @override List<Object?> get props => [error]; }
```
Use `Equatable` or freezed for value equality. Otherwise `emit` of an "equal" state still rebuilds and `bloc_test` expectations fail.

## Cubit template
```dart
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
      addError(e, s);                 // reaches BlocObserver for logging
      if (!isClosed) emit(TodosFailure(e));
    }
  }
}
```

## Wiring (VGV Page/View split)
```dart
class TodosPage extends StatelessWidget {            // route + DI
  const TodosPage({super.key});
  @override
  Widget build(BuildContext context) => BlocProvider(
        create: (context) => TodosCubit(repository: context.read<TodoRepository>())..load(),
        child: const TodosView(),
      );
}
class TodosView extends StatelessWidget {            // pure UI, test it with a mocked cubit
  @visibleForTesting
  const TodosView({super.key});
  @override
  Widget build(BuildContext context) => switch (context.watch<TodosCubit>().state) {
        TodosInitial() || TodosInProgress() => const Center(child: CircularProgressIndicator()),
        TodosSuccess(:final todos) => TodoList(todos: todos),
        TodosFailure() => const ErrorView(),
      };
}
```
- `BlocBuilder`/`context.watch` for UI, `BlocListener` for side effects (navigation, snackbar), `BlocSelector`/`context.select` to narrow rebuilds.
- One-off effects that aren't state: `bloc_presentation` (`emitPresentation(event)` + `BlocPresentationListener`). Or, for single-class state, a `BlocListener` with `listenWhen: (p, c) => p.status != c.status`.
- Repositories are provided above the app with `RepositoryProvider`/`MultiRepositoryProvider`. Blocs never depend on other blocs directly; they communicate through repositories (streams) or the UI layer.

## Event transformers (bloc_concurrency)
`on<SearchChanged>(_onSearch, transformer: restartable())` for search (cancels the previous request), `droppable()` to ignore taps while one is running, `sequential()` to queue. Default is `concurrent`. Choose on purpose, since the wrong one causes race conditions.

## Testing
```dart
blocTest<TodosCubit, TodosState>(
  'emits [InProgress, Success] when load succeeds',
  build: () => TodosCubit(repository: _MockTodoRepository()..stubFetchAll([todo])),
  act: (cubit) => cubit.load(),
  expect: () => [const TodosInProgress(), TodosSuccess([todo])],
);
```

## v9 changes to know
- `BlocOverrides` removed → set `Bloc.observer = AppBlocObserver();` and `Bloc.transformer` directly.
- hydrated_bloc: `HydratedBloc.storage = await HydratedStorage.build(storageDirectory: ...)` (v10/v11 changed storage APIs again; check bloclibrary.dev/migration).
