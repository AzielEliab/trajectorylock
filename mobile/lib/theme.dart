import 'package:flutter/material.dart';

/// Paper and charcoal surfaces. Gold is the accent. Light and dark follow the system.
const Color kMatteBlack = Color(0xFF0E0E0C);
const Color kSurface = Color(0xFF171714);
const Color kGold = Color(0xFFC9A227);
const Color kGoldInk = Color(0xFF1A1506);
const Color kIvory = Color(0xFFF3EFE4);
const Color kPaper = Color(0xFFF4F1EA);
const Color kInk = Color(0xFF1C1915);

ButtonStyle _goldFocus(ButtonStyle base) {
  return base.copyWith(
    minimumSize: const WidgetStatePropertyAll(Size(64, 48)),
    side: WidgetStateProperty.resolveWith((states) {
      if (states.contains(WidgetState.focused)) {
        return const BorderSide(color: kGold, width: 2);
      }
      return base.side?.resolve(states);
    }),
  );
}

ThemeData _theme({required ColorScheme scheme, required Color scaffold}) {
  final base = ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: scaffold,
    focusColor: kGold,
    appBarTheme: AppBarTheme(
      backgroundColor: scaffold,
      foregroundColor: scheme.onSurface,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: scheme.surface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(color: scheme.outlineVariant),
      ),
    ),
  );
  return base.copyWith(
    filledButtonTheme: FilledButtonThemeData(
      style: _goldFocus(
        FilledButton.styleFrom(
          backgroundColor: kGold,
          foregroundColor: kGoldInk,
          textStyle: const TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: _goldFocus(
        OutlinedButton.styleFrom(
          foregroundColor: scheme.onSurface,
          side: BorderSide(color: scheme.outlineVariant),
        ),
      ),
    ),
  );
}

ThemeData buildLightTheme() {
  return _theme(
    scaffold: kPaper,
    scheme: const ColorScheme.light(
      primary: kGold,
      onPrimary: kGoldInk,
      secondary: Color(0xFF8A7219),
      onSecondary: kInk,
      surface: Color(0xFFFFFDF8),
      onSurface: kInk,
      outlineVariant: Color(0xFFE3D9C6),
    ),
  );
}

ThemeData buildDarkTheme() {
  return _theme(
    scaffold: kMatteBlack,
    scheme: const ColorScheme.dark(
      primary: kGold,
      onPrimary: kGoldInk,
      secondary: Color(0xFF8A7219),
      onSecondary: kIvory,
      surface: kSurface,
      onSurface: kIvory,
      outlineVariant: Color(0xFF323026),
    ),
  );
}

/// Dark theme kept for callers that still ask for a single theme.
ThemeData buildAppTheme() => buildDarkTheme();
