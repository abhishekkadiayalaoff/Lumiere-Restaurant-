// burger_hero_page.dart
// Requires: google_fonts (pubspec.yaml) and Flutter 3.27+ (uses Color.withValues).
//
// A luxury dark hero page with a fully procedural 3D burger (no image assets):
//  - drag left/right to spin, drag up/down to change the viewing angle
//  - tap to pull the burger apart, tap again to stack it
//  - the burger assembles itself once on load
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class Palette {
  static const char = Color(0xFF121316);
  static const ember = Color(0xFFC8151B);
  static const glow = Color(0xFF4A0C10);
  static const gold = Color(0xFFCDAE72);
  static const cream = Color(0xFFF3ECE0);
}

class BurgerHeroPage extends StatefulWidget {
  const BurgerHeroPage({super.key, required this.onGetStarted});

  /// Called by the CTA, e.g. `() => Navigator.pushReplacement(...)`.
  final VoidCallback onGetStarted;

  @override
  State<BurgerHeroPage> createState() => _BurgerHeroPageState();
}

class _BurgerHeroPageState extends State<BurgerHeroPage>
    with TickerProviderStateMixin {
  late final _intro = AnimationController(
      vsync: this, duration: const Duration(milliseconds: 1800))
    ..forward();
  late final _idle =
      AnimationController(vsync: this, duration: const Duration(seconds: 14));
  late final _pull = AnimationController(
      vsync: this, duration: const Duration(milliseconds: 750));

  double _yaw = 0;
  double _tilt = 0.85; // radians: 0 = side view, pi/2 = top view
  bool _apart = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.of(context).disableAnimations) {
      _idle.stop();
      _intro.value = 1;
    } else if (!_idle.isAnimating) {
      _idle.repeat();
    }
  }

  @override
  void dispose() {
    _intro.dispose();
    _idle.dispose();
    _pull.dispose();
    super.dispose();
  }

  void _togglePull() {
    _apart = !_apart;
    _apart ? _pull.forward() : _pull.reverse();
  }

  @override
  Widget build(BuildContext context) {
    final fade = CurvedAnimation(
        parent: _intro, curve: const Interval(0.55, 1, curve: Curves.easeOut));

    return Scaffold(
      backgroundColor: Palette.char,
      body: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: RadialGradient(
            center: Alignment(0, -0.25),
            radius: 0.95,
            colors: [Palette.glow, Palette.char],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              Expanded(
                child: Stack(
                  children: [
                    const Align(
                      alignment: Alignment.topCenter,
                      child: Padding(
                        padding: EdgeInsets.fromLTRB(20, 16, 20, 0),
                        child: _Wordmark(),
                      ),
                    ),
                    Positioned.fill(
                      child: GestureDetector(
                        behavior: HitTestBehavior.opaque,
                        onTap: _togglePull,
                        onPanUpdate: (d) => setState(() {
                          _yaw += d.delta.dx * 0.012;
                          _tilt = (_tilt - d.delta.dy * 0.008).clamp(0.5, 1.15);
                        }),
                        child: AnimatedBuilder(
                          animation: Listenable.merge([_intro, _idle, _pull]),
                          builder: (_, __) {
                            final assemble =
                                1 - Curves.easeOutCubic.transform(_intro.value);
                            final pull =
                                Curves.easeInOutCubic.transform(_pull.value);
                            return CustomPaint(
                              size: Size.infinite,
                              painter: _BurgerPainter(
                                yaw: _yaw + _idle.value * 2 * math.pi,
                                tilt: _tilt,
                                spread: math.max(assemble, pull),
                                bob: math.sin(_idle.value * 2 * math.pi * 4) * 6,
                              ),
                            );
                          },
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              FadeTransition(
                opacity: fade,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(28, 8, 28, 24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'Stacked to order',
                        style: GoogleFonts.bodoniModa(
                            fontSize: 32,
                            fontWeight: FontWeight.w600,
                            color: Palette.cream),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Two smashed patties, aged cheddar and a brioche bun baked at dawn.',
                        textAlign: TextAlign.center,
                        style: GoogleFonts.manrope(
                            fontSize: 14,
                            height: 1.5,
                            color: Palette.cream.withValues(alpha: 0.65)),
                      ),
                      const SizedBox(height: 22),
                      SizedBox(
                        width: double.infinity,
                        height: 56,
                        child: FilledButton(
                          onPressed: widget.onGetStarted,
                          style: FilledButton.styleFrom(
                            backgroundColor: Palette.ember,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(6),
                              side: BorderSide(
                                  color: Palette.gold.withValues(alpha: 0.6),
                                  width: 0.8),
                            ),
                          ),
                          child: Text('Order now',
                              style: GoogleFonts.manrope(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 0.4)),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Drag to turn it. Tap to pull it apart.',
                        style: GoogleFonts.manrope(
                            fontSize: 12,
                            color: Palette.gold.withValues(alpha: 0.8)),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Wordmark extends StatelessWidget {
  const _Wordmark();

  @override
  Widget build(BuildContext context) {
    return ShaderMask(
      blendMode: BlendMode.srcIn,
      shaderCallback: (r) => LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          Palette.cream.withValues(alpha: 0.9),
          Palette.cream.withValues(alpha: 0.06),
        ],
      ).createShader(r),
      child: FittedBox(
        child: Text(
          'BURGER',
          style: GoogleFonts.bodoniModa(
              fontSize: 120,
              fontWeight: FontWeight.w800,
              letterSpacing: 6,
              height: 1,
              color: Colors.white),
        ),
      ),
    );
  }
}

class _Layer {
  const _Layer(this.th, this.r, this.top, this.edge,
      {this.amp = 0, this.waves = 0, this.grill = false});
  final double th; // thickness
  final double r; // radius factor
  final Color top, edge;
  final double amp; // wavy edge amplitude
  final int waves;
  final bool grill;
}

class _BurgerPainter extends CustomPainter {
  _BurgerPainter(
      {required this.yaw,
      required this.tilt,
      required this.spread,
      required this.bob});

  final double yaw, tilt, spread, bob;

  // Bottom to top. The dome bun is drawn separately.
  static const _layers = <_Layer>[
    _Layer(24, 0.98, Color(0xFFE2A04A), Color(0xFFA9631F)),
    _Layer(22, 0.94, Color(0xFF6A3B24), Color(0xFF2E1810), grill: true),
    _Layer(5, 1.06, Color(0xFFF4B92E), Color(0xFFC8871A), amp: 0.035, waves: 4),
    _Layer(7, 0.96, Color(0xFFD62828), Color(0xFF8F1414)),
    _Layer(22, 0.94, Color(0xFF6A3B24), Color(0xFF2E1810), grill: true),
    _Layer(6, 1.10, Color(0xFF8CC63F), Color(0xFF4E8A1E), amp: 0.07, waves: 13),
  ];

  Path _blob(Offset c, double rx, double ry, [double amp = 0, int waves = 0]) {
    final p = Path();
    const n = 96;
    for (var i = 0; i <= n; i++) {
      final a = 2 * math.pi * i / n;
      final w = 1 + amp * math.sin(a * waves + yaw * 2);
      final o = Offset(c.dx + rx * w * math.cos(a), c.dy + ry * w * math.sin(a));
      i == 0 ? p.moveTo(o.dx, o.dy) : p.lineTo(o.dx, o.dy);
    }
    return p..close();
  }

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final rx = math.min(size.width * 0.42, size.height * 0.40);
    final ry = rx * math.sin(tilt);
    final kk = math.cos(tilt);
    final gap = rx * 0.30 * spread;
    final domeReal = rx * 0.62;
    final skirt = 10 * kk;

    var stackH = domeReal * kk + skirt + gap * _layers.length;
    for (final l in _layers) {
      stackH += l.th * kk;
    }
    final y0 = size.height / 2 + stackH / 2 + ry * 0.35 + bob;

    // Ground glow
    canvas.drawOval(
      Rect.fromCenter(
          center: Offset(cx, y0 - bob + ry * 0.25 + 18),
          width: rx * 2.1,
          height: ry * 1.1 + 10),
      Paint()
        ..color = Palette.ember.withValues(alpha: 0.45)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 32),
    );

    var cursor = y0;
    for (final l in _layers) {
      final h = l.th * kk;
      final ytop = cursor - h;
      _slab(canvas, Offset(cx, ytop), rx * l.r, ry * l.r, h, l);
      if (l.grill) _grill(canvas, Offset(cx, ytop), rx * l.r, ry * l.r);
      cursor = ytop - gap;
    }
    _dome(canvas, cx, cursor - skirt, rx, ry, kk, domeReal, skirt);
  }

  void _slab(Canvas c, Offset top, double rx, double ry, double h, _Layer l) {
    for (var s = h; s > 0; s -= 2) {
      c.drawPath(
        _blob(top.translate(0, s), rx, ry, l.amp, l.waves),
        Paint()..color = Color.lerp(l.top, l.edge, s / h)!,
      );
    }
    c.drawPath(
      _blob(top, rx, ry, l.amp, l.waves),
      Paint()
        ..shader = RadialGradient(
          center: const Alignment(-0.25, -0.35),
          colors: [Color.lerp(l.top, Colors.white, 0.22)!, l.top],
        ).createShader(
            Rect.fromCenter(center: top, width: rx * 2.2, height: ry * 2.2)),
    );
  }

  void _grill(Canvas c, Offset top, double rx, double ry) {
    final rnd = math.Random(4);
    for (var i = 0; i < 26; i++) {
      final a = rnd.nextDouble() * 2 * math.pi + yaw;
      final r = math.sqrt(rnd.nextDouble()) * 0.85;
      final p = Offset(top.dx + r * rx * math.cos(a), top.dy + r * ry * math.sin(a));
      c.drawOval(
        Rect.fromCenter(center: p, width: rx * 0.06, height: ry * 0.05 + 1),
        Paint()
          ..color = (i.isEven ? Colors.black : const Color(0xFFB77A4E))
              .withValues(alpha: 0.28),
      );
    }
  }

  void _dome(Canvas c, double cx, double ybase, double rx, double ry, double kk,
      double domeReal, double skirt) {
    const low = Color(0xFFB06A22), high = Color(0xFFEDB255);
    for (var s = skirt; s >= 0; s -= 2) {
      c.drawPath(_blob(Offset(cx, ybase + s), rx, ry),
          Paint()..color = const Color(0xFF8A4E17));
    }
    const steps = 30;
    for (var i = 0; i < steps; i++) {
      final t = i / steps;
      final rad = math.sqrt(1 - t * t);
      c.drawPath(
        _blob(Offset(cx, ybase - t * domeReal * kk), rx * rad, ry * rad),
        Paint()..color = Color.lerp(low, high, t)!,
      );
    }
    // Sesame seeds (golden-angle spiral), hidden when facing away
    final seed = Paint()..color = const Color(0xFFF6E6C0);
    for (var j = 0; j < 26; j++) {
      final a = j * 2.39996 + yaw;
      final r = math.sqrt((j + 0.5) / 26) * 0.8;
      final t = math.sqrt(1 - r * r);
      if (r * math.sin(a) * kk + t * math.sin(tilt) <= 0.05) continue;
      final p = Offset(cx + r * rx * math.cos(a),
          ybase - t * domeReal * kk + r * ry * math.sin(a));
      c.save();
      c.translate(p.dx, p.dy);
      c.rotate(a);
      c.drawOval(
          Rect.fromCenter(
              center: Offset.zero,
              width: rx * 0.07,
              height: rx * 0.035 * (0.5 + t * 0.5)),
          seed);
      c.restore();
    }
    // Specular sheen
    c.drawOval(
      Rect.fromCenter(
          center: Offset(cx - rx * 0.28, ybase - domeReal * kk * 0.8),
          width: rx * 0.5,
          height: ry * 0.35 + 6),
      Paint()
        ..color = Colors.white.withValues(alpha: 0.22)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 12),
    );
  }

  @override
  bool shouldRepaint(covariant _BurgerPainter o) => true;
}
