import 'package:flutter/material.dart';

import 'theme.dart';

const notes =
    'THIS IS: research prototype / auditable geometric test. '
    'Compatibility vs declared official line. Independence groups so copies '
    "don't inflate certainty. CLI + local workbench + JSON API. "
    'THIS IS NOT: a certified forensic instrument; substitute for scene '
    'reconstruction, medical findings, lab exam; shooter/intent/guilt/narrative '
    'identifier; automatic detection of invisible projectiles; face recognition. '
    'Match probability is P(match | declared model), not P(official account is true). '
    'Synthetic example results must never be represented as real-case findings. '
    'No private case facts. Author: Aziel Eliab.';

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
      theme: buildLightTheme(),
      darkTheme: buildDarkTheme(),
      themeMode: ThemeMode.system,
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
  String status =
      'The line check runs on the desktop. Open trajectorylock ui, then press Run check.';

  void say(String next) => setState(() => status = next);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('TrajectoryLock')),
      body: Align(
        alignment: Alignment.topCenter,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
            children: [
              Text(
                'Checks how close a measured line is to a claimed line.',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 20),
              FilledButton(
                onPressed: () => say(
                  'On this computer, run trajectorylock ui and press Run check. The desktop pulls the satellite frame for the place and time, then reads the line. This phone screen does not fetch imagery or compute a line.',
                ),
                child: const Text('Run check'),
              ),
              const SizedBox(height: 8),
              OutlinedButton(
                onPressed: () => say(
                  'Doctor runs on the desktop: trajectorylock doctor. It checks that install. No network.',
                ),
                child: const Text('Doctor'),
              ),
              const SizedBox(height: 20),
              Text(status),
              const SizedBox(height: 8),
              ExpansionTile(
                title: const Text('Advanced'),
                children: [
                  ListTile(
                    title: const Text('Load example'),
                    onTap: () => say(
                      'Load example on the desktop workbench. The phone does not store the case.',
                    ),
                  ),
                  ListTile(
                    title: const Text('Import'),
                    onTap: () => say(
                      'Import JSON on the desktop workbench. This phone screen does not store media.',
                    ),
                  ),
                  ListTile(
                    title: const Text('Export'),
                    onTap: () => say(
                      'Export writes a JSON receipt from the desktop workbench.',
                    ),
                  ),
                  ListTile(
                    title: const Text('Verify'),
                    onTap: () => say(
                      'Verify fingerprints the case JSON on the desktop. It checks that the file did not change.',
                    ),
                  ),
                ],
              ),
              ExpansionTile(
                title: const Text('Notes'),
                children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                    child: Text(notes),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                'Aziel Eliab · Apache-2.0 · doi:10.5281/zenodo.22258015',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
