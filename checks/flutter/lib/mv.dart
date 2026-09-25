import 'package:flutter/material.dart';
import 'command.dart';
import 'result.dart';

class Booking { const Booking(this.id); final int id; }
abstract interface class BookingRepository { Future<Result<List<Booking>>> getBookings(); }

class BookingViewModel extends ChangeNotifier {
  BookingViewModel({required BookingRepository bookingRepository}) : _repo = bookingRepository {
    load = Command0(_load)..execute();
    delete = Command1(_delete);
  }
  final BookingRepository _repo;
  late final Command0<void> load;
  late final Command1<void, int> delete;

  List<Booking> _bookings = const [];
  List<Booking> get bookings => _bookings;

  Future<Result<void>> _load() async {
    final result = await _repo.getBookings();
    if (result case Ok(:final value)) _bookings = value;
    notifyListeners();
    return result;
  }
  Future<Result<void>> _delete(int id) async => const Result.ok(null);
}

Widget view(BookingViewModel viewModel) => ListenableBuilder(
  listenable: viewModel.load,
  builder: (context, child) {
    if (viewModel.load.running) return const Center(child: CircularProgressIndicator());
    if (viewModel.load.error) return TextButton(onPressed: viewModel.load.execute, child: const Text('retry'));
    return child!;
  },
  child: ListenableBuilder(listenable: viewModel, builder: (context, _) => Text('${viewModel.bookings.length}')),
);
