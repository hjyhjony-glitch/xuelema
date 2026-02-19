/// 设置页面（简化版）
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  @override
  Widget build(BuildContext context) {
    
    
    return Scaffold(
      appBar: AppBar(title: Text(context.l10n.settings)),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          _buildSection(context.l10n.general, [
            _buildItem(Icons.notifications, context.l10n.notificationSettings, () {}),
            _buildItem(Icons.dark_mode, context.l10n.darkMode, () {}),
            _buildItem(Icons.language, context.l10n.languageSettings, () {}),
          ]),
          SizedBox(height: 16),
          _buildSection(context.l10n.aboutSection, [
            _buildItem(Icons.info, context.l10n.versionInfo, () {}),
            _buildItem(Icons.help, context.l10n.helpCenter, () {}),
          ]),
        ],
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(padding: EdgeInsets.only(bottom: 8), child: Text(title, style: TextStyle(fontSize: 14, color: Colors.grey))),
        Card(child: Column(children: children)),
      ],
    );
  }

  Widget _buildItem(IconData icon, String title, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      trailing: Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
}
