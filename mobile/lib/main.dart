import 'package:flutter/material.dart';

import 'theme.dart';

const limitation =
    'THIS IS a research prototype / auditable geometric test. '
    'Compatibility vs the claimed line. Independence groups so copies '
    'do not inflate certainty. THIS IS NOT a certified forensic instrument, '
    'a shooter identifier, or a substitute for scene reconstruction. '
    'It does not identify a shooter, intent, or guilt. '
    'Match chance is P(match | declared model). Author Aziel Eliab.';

void main() {
  runApp(const TrajectoryLockApp());
}

class TrajectoryLockApp extends StatelessWidget {
  const TrajectoryLockApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TrajectoryLock',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const WorkbenchPage(),
    );
  }
}

class WorkbenchPage extends StatefulWidget {
  const WorkbenchPage({super.key});

  @override
  State<WorkbenchPage> createState() => _WorkbenchPageState();
}

class _WorkbenchPageState extends State<WorkbenchPage> {
  String kid =
      'How close is this line to the claimed line? Load JSON. Run check. See the result. '
      'Three separate numbers. Full analysis is the desktop package. Not a certified instrument.';
  String compat = '—';
  String match = '—';
  String evidence = '—';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('TrajectoryLock')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(limitation, style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 12),
          const Text('certified instrument: False · author: Aziel Eliab'),
          const SizedBox(height: 16),
          Text('Compatibility (how close is this line to the claimed line): $compat'),
          Text('Match chance P(match | declared model): $match'),
          Text('How strong is the evidence: $evidence'),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              FilledButton(
                onPressed: () {
                  setState(() {
                    kid =
                        'Loaded synthetic example. Not a real case. Tap Run check on the desktop workbench.';
                  });
                },
                child: const Text('Load example'),
              ),
              FilledButton(
                onPressed: () {
                  setState(() {
                    kid = 'Import JSON on the desktop workbench. This phone screen does not store media.';
                  });
                },
                child: const Text('Import'),
              ),
              FilledButton(
                onPressed: () {
                  setState(() {
                    compat = 'local';
                    match = 'local';
                    evidence = 'local';
                    kid =
                        'Run check on the desktop workbench. This phone screen does not claim a courtroom result. It does not name a shooter, intent, or guilt.';
                  });
                },
                child: const Text('Run check'),
              ),
              FilledButton(
                onPressed: () {
                  setState(() {
                    kid = 'Export is a JSON receipt on the desktop. Guardrail always included.';
                  });
                },
                child: const Text('Export'),
              ),
              FilledButton(
                onPressed: () {
                  setState(() {
                    kid =
                        'Verify: fingerprint of the case JSON. Doctor: self-check in plain words. Neither names a shooter, intent, or guilt.';
                  });
                },
                child: const Text('Verify'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(kid),
          const SizedBox(height: 24),
          const Text(
            'Not a store listing. Full engine is Python + NumPy on the desktop. Apache-2.0. '
            'Paper doi:10.5281/zenodo.22258015',
          ),
        ],
      ),
    );
  }
}
