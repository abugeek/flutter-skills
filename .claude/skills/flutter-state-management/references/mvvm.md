# Flutter-official MVVM (docs.flutter.dev/app-architecture, Compass sample app) — verified 2026-09-25

The Flutter team's recommended architecture: **View + ViewModel (UI layer) → Repository + Service (data layer)**, with `ChangeNotifier` ViewModels, `provider` for DI, **Commands** for user actions, and a **Result** type instead of throwing.

## Result (from flutter/samples compass_app/lib/utils/result.dart)
```dart
sealed class Result<T> {
  const Result();
  const factory Result.ok(T value) = Ok._;
  const factory Result.error(Exception error) = Error._;
}
final class Ok<T> extends Result<T> { const Ok._(this.value); final T value; }
final class Error<T> extends Result<T> { const Error._(this.error); final Exception error; }
```
Repositories return `Future<Result<T>>`. Callers `switch` on it, so errors can't be forgotten.

## Command (compass_app/lib/utils/command.dart, abridged)
```dart
abstract class Command<T> extends ChangeNotifier {
  bool _running = false;
  bool get running => _running;
  Result<T>? _result;
  bool get error => _result is Error;
  bool get completed => _result is Ok;
  Result? get result => _result;
  void clearResult() { _result = null; notifyListeners(); }

  Future<void> _execute(Future<Result<T>> Function() action) async {
    if (_running) return;                 // blocks double taps
    _running = true; _result = null; notifyListeners();
    try { _result = await action(); } finally { _running = false; notifyListeners(); }
  }
}
class Command0<T> extends Command<T> {
  Command0(this._action); final Future<Result<T>> Function() _action;
  Future<void> execute() => _execute(_action);
}
class Command1<T, A> extends Command<T> {
  Command1(this._action); final Future<Result<T>> Function(A) _action;
  Future<void> execute(A arg) => _execute(() => _action(arg));
}
```

## ViewModel + View
```dart
class BookingViewModel extends ChangeNotifier {
  BookingViewModel({required BookingRepository bookingRepository}) : _repo = bookingRepository {
    load = Command0(_load)..execute();
    delete = Command1(_delete);
  }
  final BookingRepository _repo;
  late final Command0<void> load;
  late final Command1<void, int> delete;

  List<Booking> _bookings = const [];
  List<Booking> get bookings => _bookings;         // UI reads immutable data only

  Future<Result<void>> _load() async {
    final result = await _repo.getBookings();
    if (result case Ok(:final value)) _bookings = value;
    notifyListeners();
    return result;
  }
  Future<Result<void>> _delete(int id) async { /* ... */ return const Result.ok(null); }
}

// View: logic-free; only simple ifs, layout, animation and routing
ListenableBuilder(
  listenable: viewModel.load,
  builder: (context, child) {
    if (viewModel.load.running) return const Center(child: CircularProgressIndicator());
    if (viewModel.load.error) return ErrorIndicator(onRetry: viewModel.load.execute);
    return child!;
  },
  child: ListenableBuilder(listenable: viewModel, builder: (context, _) => BookingList(viewModel.bookings)),
)
```
- One-off effects: in the View's `initState`, `viewModel.delete.addListener(_onResult)`. Show the snackbar when `completed`/`error`, then `clearResult()`. Remove the listener in `dispose`.
- ViewModels are created in the route builder and get repositories from `context.read()` (provider). They're never created inside `build()`, and they never take a `BuildContext`.

## Rules from the official recommendations table
Strongly recommended: separate UI and data layers; repository pattern; MVVM with "dumb" widgets; no logic in widgets; unidirectional data flow; immutable models; DI with `provider`; **abstract repository classes** (enable fakes and dev/staging implementations); unit tests for every service/repository/ViewModel; widget tests for views; **fakes over mocks**.
Recommended: Commands; freezed/built_value for models; go_router; naming by role (`HomeViewModel`, `HomeScreen`, `UserRepository`, `ClientApiService`); shared widgets in `ui/core/`, not `/widgets`.
Conditional: a domain layer / use-cases only if the logic is complex or repeated across ViewModels; separate API models vs domain models only in large apps; ChangeNotifier itself (any state library is acceptable).
