# Flutter breaking changes & migrations (generated)

Generated 2026-09-25 from docs.flutter.dev/release/breaking-changes by `update.py`. Do not edit by hand.
Run `dart fix --apply` first (column `dart fix`), then fix the rest manually.

## 3.47 · OpenGL ES render-to-texture content is stored top-down
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/opengles-render-to-texture-top-down

Shaders written for OpenGL ES often flipped the Y coordinate inside an `IMPELLER_TARGET_OPENGLES` block to make render-target textures match the other backends. Render-target textures are now top-down on every backend, so that flip is no longer needed.

## 3.47 · Update semantics header and headingLevel behavior on iOS and Android
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/semantics-header-heading-level

If your code previously used `Semantics(header: true, ...)` or `SemanticsProperties(header: true, ...)` to declare headings, migrate your code to use `headingLevel: 1` (or another integer greater than `0`).

## 3.47 · Removal of `describeEnum`
dart fix: no · https://docs.flutter.dev/release/breaking-changes/remove-describeEnum

If your code previously used the `describeEnum` method to get the value name of an enum member, migrate your code to use the `name` getter on the instance itself.

```dart
// before
final theme = describeEnum(Theme.light);
// after
Theme.light.name;
```

## 3.44 · Changing RawMenuAnchor close order
dart fix: no · https://docs.flutter.dev/release/breaking-changes/raw-menu-anchor-close-order

If your code does not override the default implementation of `RawMenuAnchor.onCloseRequested` or your `RawMenuAnchor` does not contain submenus, no changes are required.

```dart
// before
RawMenuAnchor(
  controller: menuController,
  onCloseRequested: (hideOverlay) {
    if (!animationController.isForwardOrCompleted) {
      return;
    }

    // Descendant submenus must be closed before the parent menu.
// after
RawMenuAnchor(
  controller: menuController,
  onCloseRequested: (hideOverlay) {
    if (!animationController.isForwardOrCompleted) {
      return;
    }

    // `menuController.closeChildren()` is now called automatically.
```

## 3.44 · Deprecate `onReorder` callback
dart fix: no · https://docs.flutter.dev/release/breaking-changes/deprecate-onreorder-callback

The `ReorderableListView`, `ReorderableListView.builder`, `ReorderableList`, and `SliverReorderableList` widgets share the same reordering logic. The same migration steps apply to each of these widgets.

```dart
// before
onReorder: (int oldIndex, int newIndex) {
if (oldIndex < newIndex) {
newIndex -= 1;
}
// after
onReorderItem: (int oldIndex, int newIndex) {
```

## 3.44 · Deprecate `TextInputConnection.setStyle`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/deprecate-text-input-connection-set-style

If you author a custom text input client, replace calls to `TextInputConnection.setStyle` with `TextInputConnection.updateStyle`.

```dart
// before
connection.setStyle(
  fontFamily: 'Roboto',
  fontSize: 14.0,
  fontWeight: FontWeight.normal,
  textDirection: TextDirection.ltr,
  textAlign: TextAlign.start,
);
// after
connection.updateStyle(
  TextInputStyle(
    fontFamily: 'Roboto',
    fontSize: 14.0,
    fontWeight: FontWeight.normal,
    textDirection: TextDirection.ltr,
    textAlign: TextAlign.start,
    letterSpacing: 1.2,
```

## 3.44 · Deprecated `cacheExtent` and `cacheExtentStyle`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/scroll-cache-extent

The `cacheExtent` and `cacheExtentStyle` properties are deprecated.

## 3.44 · `IconData` class marked as `final`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/icondata-class-marked-final

Instead of implementing `IconData`, such as with an `enum` that supports dot shorthand, type safety, and an automated `.values` list, use a wrapper class with `static const` instances.

```dart
// before
enum AppIcons implements IconData {
  arrowUpward(0xe062),
  arrowDownward(0xe061);

  const AppIcons(this.codePoint)
    : fontFamily = 'MaterialIcons',
      fontPackage = null,
      matchTextDirection = false;
// after
final class AppIconData {
  final IconData iconData;

  const AppIconData._(this.iconData);

  static const arrowUpward = AppIconData._(
    IconData(0xe062, fontFamily: 'MaterialIcons'),
  );
```

## 3.44 · Large screen orientation and resizability restrictions ignored on Android 17
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/android-large-screens-restrictions-ignored

For apps targeting Android 17 or higher,

## 3.44 · ListTile reports an error in debug when wrapped in a colored widget
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/list-tile-color-warning

To fix the error, remove the background color from the intermediate widget or wrap the `ListTile` in its own `Material` widget.

```dart
// before
// The colored Container hides the ink splashes from the ListTile.
Material(
  child: Container(
    color: Colors.pink,
    child: ListTile(
      title: const Text('Title'),
      onTap: () {},
    ),
// after
// Use a Material widget directly for the background color.
Material(
  color: Colors.pink,
  child: Container(
    child: ListTile(
      title: const Text('Title'),
      onTap: () {},
    ),
```

## 3.44 · Migrating Flutter Android projects to built-in Kotlin
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/migrate-to-built-in-kotlin



## 3.44 · Page transition builders reorganization
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/decouple-page-transition-builders

If you use `CupertinoPageTransitionsBuilder` and only import `package:flutter/material.dart`, add an import for `package:flutter/cupertino.dart`.

```dart
// before
import 'package:flutter/material.dart';

final pageTransitionsTheme = PageTransitionsTheme(
  builders: {
    TargetPlatform.android: ZoomPageTransitionsBuilder(),
    TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
  },
);
// after
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

final pageTransitionsTheme = PageTransitionsTheme(
  builders: {
    TargetPlatform.android: ZoomPageTransitionsBuilder(),
    TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
  },
```

## 3.41 · Merged threads on Linux
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/linux-merged-threads

Merged threads shouldn't affect your app.

## 3.41 · `FontWeight` also controls the weight attribute of variable fonts
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/font-weight-variation

Applications may see changes in text rendering if they used variable fonts and were specifying `FontWeight` in text styles without a matching `FontVariation('wght')` value.

## 3.41 · Deprecate `containsSemantics` in favor of `isSemantics`
dart fix: yes · https://docs.flutter.dev/release/breaking-changes/deprecate-contains-semantics

To automatically migrate your code, run the following command:

```dart
// before
expect(
  tester.getSemantics(find.byType(MyWidget)),
  containsSemantics(
    label: 'My Widget',
    isButton: true,
  ),
);
// after
expect(
  tester.getSemantics(find.byType(MyWidget)),
  isSemantics(
    label: 'My Widget',
    isButton: true,
  ),
);
```

## 3.41 · Deprecate `findChildIndexCallback` in favor of `findItemIndexCallback` in `ListView` and `SliverList` separated constructors
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/separated-builder-find-child-index-callback

To migrate from `findChildIndexCallback` to `findItemIndexCallback`, replace the parameter name and remove any index multiplications that were used to account for separators.

```dart
// before
ListView.separated(
  itemCount: items.length,
  findChildIndexCallback: (Key key) {
    final ValueKey<String> valueKey = key as ValueKey<String>;
    final int itemIndex = items.indexOf(valueKey.value);
    // Multiply by 2 to account for separators.
    return itemIndex == -1 ? null : itemIndex * 2;
  },
// after
ListView.separated(
  itemCount: items.length,
  findItemIndexCallback: (Key key) {
    final ValueKey<String> valueKey = key as ValueKey<String>;
    final int itemIndex = items.indexOf(valueKey.value);
    // Return item index directly - no need to multiply by 2.
    return itemIndex == -1 ? null : itemIndex;
  },
```

## 3.41 · Material 3 tokens update
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/material-color-utilities

In general, we believe the colors generated will be more legible and visually appealing, but if you want to maintain the previous colors when upgrading, you will have to manually set those properties to their desired color after generating.

## 3.38 · `CupertinoDynamicColor` wide gamut support
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/wide-gamut-cupertino-dynamic-color

Addressing previously missed deprecations in CupertinoDynamicColor to

## 3.38 · Deprecate `OverlayPortal.targetsRootOverlay`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/deprecate-overlay-portal-targets-root

If you are using `OverlayPortal.targetsRootOverlay`, use `OverlayPortal` with `overlayLocation` instead.

```dart
// before
Widget build(BuildContext context) {
  return OverlayPortal.targetsRootOverlay(
    controller: myController,
    overlayChildBuilder: _myBuilder,
    child: myChild,
  );
}
// after
Widget build(BuildContext context) {
  Overlay.of(context);
  // ...
}
```

## 3.38 · Deprecate `SemanticsProperties.focusable` and `SemanticsConfiguration.isFocusable`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/deprecate-focusable

Replace `SemanticsConfiguration.isFocusable` with `SemanticsConfiguration.isFocused`.

```dart
// before
void describeSemanticsConfiguration(SemanticsConfiguration config) {
  config.isFocusable = true;
  config.isFocused = true;
}
// after
void describeSemanticsConfiguration(SemanticsConfiguration config) {
  config.isFocused = true;
}
```

## 3.38 · SnackBar with action no longer auto-dismisses
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/snackbar-with-action-behavior-update

To restore the old auto-dismiss behavior for a SnackBar with an action, set `persist` to `false`.

## 3.38 · The default page transition on Android is now `PredictiveBackPageTransitionBuilder`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/default-android-page-transition

If you want to keep your app's page transition on the old [`ZoomPageTransitionsBuilder`][], you can simply set your page transition explicitly in your app's theme. Keep in mind that you will not be able to support predictive back route transitions.

```dart
// before
return MaterialApp(
  theme: ThemeData(
    brightness: Brightness.light,
    // pageTransitionsTheme is the default.
  ),
  home: const MyFirstScreen(),
);
// after
MaterialApp(
  theme: ThemeData(
    // pageTransitionsTheme is explicitly set to the old transition on Android.
    pageTransitionsTheme: const PageTransitionsTheme(
      builders: {
        TargetPlatform.android: ZoomPageTransitionsBuilder(),
      },
    ),
```

## 3.38 · UISceneDelegate adoption
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/uiscenedelegate

Learn how to migrate your Flutter iOS app, add-to-app integration, or plugin

## 3.35 · Component theme normalization updates
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/component-theme-normalization-updates

In `ThemeData`: - The type of the `appBarTheme` property has been changed from `AppBarTheme` to `AppBarThemeData`. - The type of `bottomAppBarTheme` property has been changed from `BottomAppBarTheme` to `BottomAppBarThemeData`. - The type of `inputDecorationTheme` property has been changed from `Inp

```dart
// before
final AppBarTheme appBarTheme = Theme.of(context).appBarTheme;
final AppBarTheme appBarTheme = AppBarTheme.of(context);

final BottomAppBarTheme bottomAppBarTheme = Theme.of(context).bottomAppBarTheme;
final BottomAppBarTheme bottomAppBarTheme = BottomAppBarTheme.of(context);

final InputDecorationTheme inputDecorationTheme = Theme.of(context).inputDecorationTheme;
final InputDecorationTheme inputDecorationTheme = InputDecorationTheme.of(context);
// after
final AppBarThemeData appBarTheme = Theme.of(context).appBarTheme;
final AppBarThemeData appBarTheme = AppBarTheme.of(context);

final BottomAppBarThemeData bottomAppBarTheme = Theme.of(context).bottomAppBarTheme;
final BottomAppBarThemeData bottomAppBarTheme = BottomAppBarTheme.of(context);

final InputDecorationThemeData inputDecorationTheme = Theme.of(context).inputDecorationTheme;
final InputDecorationThemeData inputDecorationTheme = InputDecorationTheme.of(context);
```

## 3.35 · Deprecate `DropdownButtonFormField` `value` parameter in favor of `initialValue`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/deprecate-dropdownbuttonformfield-value

Replace the `value` parameter of the [`DropdownButtonFormField`][] constructor with the `initialValue` parameter to initialize [`DropdownButtonFormField.initialValue`][].

## 3.35 · Deprecate app bar color
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/appbar-theme-color

Replace all uses of the `color` parameter with `backgroundColor` in `AppBarTheme` and `AppBarThemeData` constructors and `copyWith` methods.

```dart
// before
// AppBarTheme constructor
AppBarTheme(
  color: Colors.blue,
  elevation: 4.0,
)

// AppBarTheme copyWith
theme.copyWith(
// after
// AppBarTheme constructor
AppBarTheme(
  backgroundColor: Colors.blue,
  elevation: 4.0,
)

// AppBarTheme copyWith
theme.copyWith(
```

## 3.35 · Removed semantics elevation and thickness
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/remove-semantics-elevation-and-thickness

If you previously assigned these properties, remove the assignments.

```dart
// before
void describeSemanticsConfiguration(SemanticsConfiguration config) {
  config.label = 'my label';
  config.elevation = 1;
  config.thickness = 1;
}
// after
void describeSemanticsConfiguration(SemanticsConfiguration config) {
  config.label = 'my label';
}
```

## 3.35 · The `Form` widget no longer supports being a sliver
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/form-semantics

If your app does not currently use the Form widget directly as a sliver within a scrollable list (e.g., as a direct child of CustomScrollView's slivers property), then no changes are required.

```dart
// before
sliver: Form(
    key: controller.formKey,
    child: SomeWidgetWithFormFields(),
)
// after
sliver: SliverToBoxAdapter(
    child: Form(
        key: controller.formKey,
        child: SomeWidgetWithFormFields(),
    )
)
```

## 3.35 · Flutter now sets default `abiFilters` in Android builds
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/default-abi-filters-android

If your app doesn't customize `abiFilters`, no changes are required.

## 3.35 · Merged threads on macOS and Windows
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/macos-windows-merged-threads

Merged threads should not affect your app.

## 3.35 · The `Visibility` widget is no longer focusable by default when `maintainState` is enabled
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/visibility-maintainfocusability

If your app has a `Visibility` widget that does not set `maintainState` to true, then no changes are required.

```dart
// before
child: Visibility(
    maintainState: true,
    child: SomeWidget(),
)
// after
child: Visibility(
    maintainState: true,
    maintainFocusability: true,
    child: SomeWidget(),
)
```

## 3.35 · `$FLUTTER_ROOT/version` replaced by `$FLUTTER_ROOT/bin/cache/flutter.version.json`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/flutter-root-version-file

Most Flutter developers don't parse or use this file, but custom tools or CI configurations might.

## 3.32 · Deprecate `SystemContextMenuController.show`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/system_context_menu_controller_show

Most users use the system context menu through the `SystemContextMenu` widget, and in this case there will be no change required. The `SystemContextMenu` widget automatically gets the default items under the hood.

```dart
// before
_controller.show(selectionRect);
// after
final List<IOSSystemContextMenuItem> defaultItems =
    SystemContextMenu.getDefaultItems(editableTextState);
final WidgetsLocalizations localizations =
    WidgetsLocalizations.of(context);
final List<IOSSystemContextMenuItemData> defaultItemData =
    defaultItems
        .map((IOSSystemContextMenuItem item) =>
            item.getData(localizations))
```

## 3.32 · Deprecate `ExpansionTileController` in favor of `ExpansibleController`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/expansion-tile-controller

To migrate, replace the `controller` parameter of an `ExpansionTile` from an `ExpansionTileController` to an `ExpansibleController`. Unlike `ExpansionTileController`, `ExpansibleController` is a `ChangeNotifier`, so remember to dispose the new `ExpansibleController`.

```dart
// before
class _MyWidgetState extends State<MyWidget> {
  final ExpansionTileController controller = ExpansionTileController();

  @override
  Widget build(BuildContext context) {
    return ExpansionTile(
      controller: controller,
    );
// after
class _MyWidgetState extends State<MyWidget> {
  final ExpansibleController controller = ExpansibleController();

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }
```

## 3.32 · Deprecate `ThemeData.indicatorColor` in favor of `TabBarThemeData.indicatorColor`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/deprecate-themedata-indicatorcolor

Replace [`ThemeData.indicatorColor`][] with [`TabBarThemeData.indicatorColor`][] to override the default tab bar indicator color when [`ThemeData.useMaterial3`][] flag is set to `false`.

```dart
// before
theme: ThemeData(
  indicatorColor: Colors.red,
  useMaterial3: false,
),
// after
theme: ThemeData(
  tabBarTheme: const TabBarThemeData(indicatorColor: Colors.red),
  useMaterial3: false,
),
```

## 3.32 · Material Theme System Updates
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/material-theme-system-updates

Previously, the type of `ThemeData.cardTheme` was `Object?` to accept both `CardTheme` and `CardThemeData`. Now that the type has been changed to `CardThemeData?`, a migration is required if `ThemeData.cardTheme` is used. Similarly, the types of `ThemeData.dialogTheme` and `ThemeData.tabBarTheme` sh

```dart
// before
final ThemeData theme = ThemeData(
    cardTheme: CardTheme(),
    dialogTheme: DialogTheme(),
    tabBarTheme: TabBarTheme(),
);
// after
final ThemeData theme = ThemeData(
    cardTheme: CardThemeData(),
    dialogTheme: DialogThemeData(),
    tabBarTheme: TabBarThemeData(),
);
```

## 3.32 · `.flutter-plugins-dependencies` replaces `.flutter-plugins`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/flutter-plugins-configuration

Most Flutter developers don't parse or use this file, but build configurations might, including the `settings.gradle` file as generated by older invocations of `flutter create --platforms android`. These legacy files might still reference `.flutter-plugins` and must be updated to a newer build scrip

## 3.32 · Localized messages are generated into source, not a synthetic package
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/flutter-generate-i10n-source

This change only affects apps that have the following entry in their `pubspec.yaml`:

## 3.32 · Changing the default `goldenFileComparator` for `integration_test`s
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/integration-test-default-golden-comparator

In most cases, we expect users to have to do nothing - this will be in a sense _new_ functionality that replaced functionality that did not work and caused an unhandled exception which would fail a test.

## 3.32 · Deprecate `InputDecoration.maintainHintHeight` in favor of `InputDecoration.maintainHintSize`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/deprecate-inputdecoration-maintainhintheight

Replace [`InputDecoration.maintainHintHeight`][] with [`InputDecoration.maintainHintSize`][] to override the default intrinsic size computation.

## 3.32 · Underdamped spring formula changed
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/spring-description-underdamped

Migration is necessary only for springs with damping ratios less than 1 and masses other than 1.

```dart
// before
const spring = SpringDescription(
  mass: 20.0,
  stiffness: 10,
  damping: 1,
);
// after
const spring = SpringDescription(
  mass: 1.0,
  stiffness: 100.499375,
  damping: 20,
);
```

## 3.29 · Removal of v1 Android embedding Java APIs
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/v1-android-embedding

Learn how to account for the removal of the Android v1 embedding APIs.

## 3.29 · Deprecate `WebGoldenComparator`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/web-golden-comparator

For most users, no changes are required (other than migrating off the HTML backend, which is not covered here), the `flutter` tool will automatically configure [`goldenFileComparator`][] and use it (when using a non-HTML web backend).

## 3.29 · Deprecate `ThemeData.dialogBackgroundColor` in favor of `DialogThemeData.backgroundColor`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/deprecate-themedata-dialogbackgroundcolor

Replace [`ThemeData.dialogBackgroundColor`][] with [`DialogThemeData.backgroundColor`][] to override the default dialog background color.

```dart
// before
theme: ThemeData(
  dialogBackgroundColor: Colors.orange,
),
// after
theme: ThemeData(
  dialogTheme: const DialogThemeData(backgroundColor: Colors.orange),
),
```

## 3.29 · `ImageFilter.blur` default tile mode automatic selection
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/image-filter-blur-tilemode

Only blur image filters that don't specify an explicit tile mode are impacted by this change.

```dart
// before
final filter = ui.ImageFilter.blur(sigmaX: 4, sigmaY: 4, tileMode: TileMode.decal);
// after
final filter = ui.ImageFilter.blur(sigmaX: 4, sigmaY: 4);
```

## 3.29 · Updated Material 3 `Slider`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/updated-material-3-slider

To opt into the updated design spec for the `Slider`, set the `year2023` flag to `false`:

## 3.29 · Updated Material 3 progress indicators
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/updated-material-3-progress-indicators

To opt into the updated design spec for the `LinearProgressIndicator`, set the `year2023` flag to `false`:

## 3.27 · `Color` wide gamut support
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/wide-gamut-framework

Changes to support wide gamut color and migration instructions.

## 3.27 · Component theme normalization
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/component-theme-normalization

In `ThemeData`:

```dart
// before
final CardTheme cardTheme = Theme.of(context).cardTheme;
final CardTheme cardTheme = CardTheme.of(context);

final DialogTheme dialogTheme = Theme.of(context).dialogTheme;
final DialogTheme dialogTheme = DialogTheme.of(context);

final TabBarTheme tabBarTheme = Theme.of(context).tabBarTheme;
final TabBarTheme tabBarTheme = TabBarTheme.of(context);
// after
final CardThemeData cardTheme = Theme.of(context).cardTheme;
final CardThemeData cardTheme = CardTheme.of(context);

final DialogThemeData dialogTheme = Theme.of(context).dialogTheme;
final DialogThemeData dialogTheme = DialogTheme.of(context);

final TabBarThemeData tabBarTheme = Theme.of(context).tabBarTheme;
final TabBarThemeData tabBarTheme = TabBarTheme.of(context);
```

## 3.27 · Deep links flag change
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/deep-links-flag-change

If you're using Flutter's default deep linking setup, this isn't a breaking change for you.

## 3.27 · Material 3 Tokens Update in Flutter
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/material-design-3-token-update

The differences in the mappings of the color roles are small. Use `ColorScheme.copyWith` to revert to the original default colors:

```dart
// before
final ColorScheme colors = ThemeData().colorScheme;
// after
final ColorScheme colors = ThemeData().colorScheme.copyWith(
  onPrimaryContainer: const Color(0xFF21005D),
  onSecondaryContainer: const Color(0xFF1D192B),
  onTertiaryContainer: const Color(0xFF31111D),
  onErrorContainer: const Color(0xFF410E0B),
);
```

## 3.27 · Remove invalid parameters for `InputDecoration.collapsed`
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/input-decoration-collapsed

To migrate, remove usage of `floatingLabelBehavior` and `floatingLabelAlignment` parameters when calling the `InputDecoration.collapsed` constructor. Those parameters had no effect.

```dart
// before
InputDecoration.collapsed(
  hintText: 'Hint',
  floatingLabelAlignment: FloatingLabelAlignment.center,
  floatingLabelBehavior: FloatingLabelBehavior.auto,
),
// after
InputDecoration.collapsed(
  hintText: 'Hint',
),
```

## 3.27 · Set default for SystemUiMode to Edge-to-Edge
dart fix: unstated · https://docs.flutter.dev/release/breaking-changes/default-systemuimode-edge-to-edge

To opt out of edge-to-edge on Android SDK 15, specify the new style attribute in each activity that requires it. If you have a parent style that child styles need to opt out of, you can modify the parent only. In the following example, update the style configuration generated from `flutter create`.
