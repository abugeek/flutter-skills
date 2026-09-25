---
name: flutter-performance
description: Flutter performance and app-size optimization (Flutter 3.47 official perf docs + LeanCode) - jank and dropped frames, excessive rebuilds, heavy build() work, isolates/compute, long lists (ListView.builder, GridView.builder, slivers, shrinkWrap), image memory (cacheWidth), Opacity/saveLayer/clipping, intrinsics, Impeller, RepaintBoundary, CustomPaint shouldRepaint, Flutter Web rebuilds, APK/IPA size analysis. Use this whenever the user reports laggy scrolling, stutter, freezes, high memory/OOM, slow startup, a big app binary, or asks to optimize or review a Flutter screen/list for performance.
---

# Flutter performance

Verified 2026-09-25 against docs.flutter.dev/perf (Flutter 3.47: Impeller is the default renderer on iOS, Android API 29+, macOS, Windows and Linux; not web).

A frame has **~16 ms at 60 Hz (~8 ms at 120 Hz)**. Almost every real Flutter performance problem is self-inflicted: too-wide rebuilds, work in `build()`, eager lists, full-resolution images, or CPU work on the UI isolate. The engine (Impeller) is rarely the bottleneck.

## Measure first

- Profile in **profile mode on a real (ideally low-end) device**. Debug-mode numbers are meaningless.
- Use DevTools Performance and the Timeline (frame times, jank), the Performance Overlay, and Memory (leaks, image cache).
- Optimize when you see dropped frames, stuttering animations, or laggy scrolling. Otherwise write clear code first. No premature optimization.

## Rebuilds

- Call `setState` as low in the tree as possible. State high up rebuilds everything below it.
- Split big widgets into **small widget classes** (not helper methods, which rebuild with the parent). Use `const` constructors wherever possible; const widgets are skipped on rebuild.
- Nothing expensive in `build()` (parsing, sorting, filtering, formatting big data). Do it in `initState`/`didUpdateWidget` (recompute only when input changed) or in the state layer.
- In Riverpod/BLoC, watch only what the widget needs (`select`, `BlocSelector`, `context.select`) so unrelated state changes don't rebuild it.
- Flutter Web is extra sensitive to deep trees and wide rebuilds. Prefer `LayoutBuilder` over `MediaQuery` to limit rebuild scope, and don't rebuild large sections on window resize.

## CPU work → isolates

`async` does not move work off the UI thread. Big `jsonDecode`, loops, and image processing go to `Isolate.run(() => parse(body))` (or `compute(fn, arg)`, which is the same on mobile/desktop). **On web there are no isolates: `compute` runs on the main thread**, so keep web payloads small or paginate. Isolates have spawn and copy overhead, so skip them for small data. Use a long-lived isolate for repeated work. Isolates can't use `rootBundle` or `dart:ui`, and plugins need `BackgroundIsolateBinaryMessenger`.

## Lists and grids

- Long or dynamic data: **`ListView.builder` / `ListView.separated` / `GridView.builder` / `SliverList`** build items lazily. Never `ListView(children: [for ...])` for real data.
- **`shrinkWrap: true` itself disables laziness.** The list must build and measure every child to know its own height, even with `.builder`. When you see it on a list longer than about a screen, remove it: give the list bounded height (`Expanded`) or combine sections with slivers.
- Avoid **intrinsic** layout (`IntrinsicHeight`/`IntrinsicWidth`, or grids and lists sizing cells to the tallest child). It adds an extra layout pass over all children. Use fixed extents (`itemExtent`, `prototypeItem`) when rows have a known height.
- `ListView`/`GridView` inside a `Column`/`Row` needs `Expanded`/`Flexible`, or you get "Vertical viewport was given unbounded height".
- Mixed scrolling content (header + list + grid): one `CustomScrollView` with slivers. Don't nest a `ListView` inside it, and don't put a big `Column` in `SliverToBoxAdapter` (that kills laziness too). `SliverToBoxAdapter` is for single elements; `SliverFillRemaining` is for empty/loading states.
- Start with `ListView`; reach for slivers only when you need collapsing headers or mixed sections.
- Grid tile proportions come from `childAspectRatio` (width/height), not from child heights.

## Images (most common OOM cause)

- Decode at display size: `Image.network(url, cacheWidth: 200)` / `cacheHeight`, or `ResizeImage`. A 4000 px photo in an 80 px thumbnail wastes megabytes per item.
- Prefer WebP assets.

## Painting and animation

- **Remove `Opacity` wrappers; don't leave them "because it's static".** `Opacity` can force an offscreen `saveLayer`. Replace it by case:
  - image → `Image(opacity: const AlwaysStoppedAnimation(0.5))` (or `color` + `colorBlendMode`)
  - text or a simple shape → draw with a semi-transparent color (`color.withValues(alpha: 0.5)`)
  - fading in or out → `FadeTransition` / `AnimatedOpacity`, or `FadeInImage` for image loading
  - only for a complex, overlapping subtree is `Opacity` acceptable.
- Clipping is cheaper than opacity but not free. Prefer the `borderRadius` a widget already has (`DecoratedBox`, `Card`, `ClipRRect` only when needed). Never use `Clip.antiAliasWithSaveLayer` unless you must. Find `saveLayer` calls in the DevTools timeline, or turn on `checkerboardOffscreenLayers` in the DevTools Performance view.
- `StringBuffer` for building strings in loops.
- Don't override `operator ==` on widgets. Rely on `const` and on reusing the same child instance (the `TransitionBuilder` / `child:` pattern) to skip rebuilds.
- Wrap frequently repainting subtrees (animations, tickers, charts) in `RepaintBoundary` so the rest doesn't repaint.
- `CustomPainter`: implement `shouldRepaint` properly (compare the inputs; `return true` repaints every frame). Keep painters pure rendering, with no layout or interaction logic, and account for device pixel ratio. For charts and custom indicators, one painter often beats composing many widgets.
- Hiding but keeping state: `Visibility(maintainState: true)` / `Offstage`. A collection `if` removes the widget and its state. In single-child slots, return `SizedBox.shrink()`, not `Container()`.
- Flutter GPU (experimental, Impeller-only, not web) is for custom 3D/particles/shaders only. Most apps never need it.

## App size

1. Measure: `flutter build apk --analyze-size` / `flutter build appbundle --analyze-size` (and open the report in DevTools).
2. Judge release builds only. Ship an **AAB** (Play serves per-device splits); `--split-per-abi` for direct APKs (often −40-50%).
3. WebP images, fewer font families/weights, remove unused plugins (they bundle native libraries).
4. Flutter apps start a few MB larger than native because of the engine; LeanCode's apps average ~11 MB (9-14 MB).

## Review checklist

1. Profiled in profile mode on a device?
2. Any work in `build()` that could be cached or moved?
3. Lists built lazily, no `shrinkWrap` on long lists, no nested scrollables?
4. Images decoded at display size?
5. `const` used, widgets split into classes, `setState` scoped low?
6. CPU-heavy work off the UI isolate?
7. `Opacity` animations, `shouldRepaint`, and `RepaintBoundary` where repaints are frequent?

## Sources

If this project has a `leancode/` folder, read `leancode/<path>.md`; otherwise fetch `https://leancode.co/<path>`.

- `glossary/flutter-app-performance-optimization`, `glossary/app-size-optimization-in-flutter`
- `glossary/listview-in-flutter`, `glossary/gridview-in-flutter`, `glossary/sliver-in-flutter`
- `glossary/conditional-rendering-in-flutter`, `glossary/custompaint-in-flutter`, `glossary/flutter-gpu`
- `glossary/asynchronous-programming-in-flutter`: isolates vs async
- `blog/flutter-coding-best-practices`: #13 build(), #14 compute(), #16 widget classes
- `blog/flutter-issues-problems-reality-check`: realistic performance/size expectations
- `blog/complex-animations-in-flutter`: CustomPainter + GestureDetector case study
