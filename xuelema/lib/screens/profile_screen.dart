/// 个人中心屏幕（完整版） - 包含定时提醒入口
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    
    return Scaffold(
      appBar: AppBar(title: Text(l10n.profileCenter)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // 用户信息卡片
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  CircleAvatar(radius: 32, child: Icon(Icons.person, size: 32)),
                  const SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(l10n.username, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      Text(l10n.normalUser),
                    ],
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.edit),
                    onPressed: () {
                      _showEditProfileDialog(context);
                    },
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // 学习统计
          _buildSectionTitle('学习统计'),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildStatItem('连续学习', '5天', Icons.star),
                      _buildStatItem('总任务', '12个', Icons.list),
                      _buildStatItem('完成率', '85%', Icons.check_circle),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildStatItem('总专注', '8小时', Icons.timer),
                      _buildStatItem('错题', '24道', Icons.error),
                      _buildStatItem('复习', '3次', Icons.replay),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // 设置
          _buildSectionTitle('设置'),
          Card(
            child: Column(
              children: [
                _buildItem(
                  icon: Icons.notifications,
                  title: '定时提醒设置',
                  subtitle: '管理学习提醒和定时通知',
                  onTap: () => Navigator.pushNamed(context, '/reminders'),
                ),
                const Divider(height: 1),
                _buildItem(
                  icon: Icons.flag,
                  title: '学习目标设置',
                  subtitle: '设置每日学习目标和计划',
                  onTap: () => Navigator.pushNamed(context, '/goals'),
                ),
                const Divider(height: 1),
                _buildItem(
                  icon: Icons.settings,
                  title: l10n.generalSettings,
                  subtitle: '应用主题、语言等设置',
                  onTap: () => _showComingSoon(context, '通用设置'),
                ),
                const Divider(height: 1),
                _buildItem(
                  icon: Icons.security,
                  title: '隐私与安全',
                  subtitle: '数据管理和权限设置',
                  onTap: () => _showComingSoon(context, '隐私与安全'),
                ),
                const Divider(height: 1),
                _buildItem(
                  icon: Icons.storage,
                  title: '数据管理',
                  subtitle: '备份、恢复和清除数据',
                  onTap: () => _showComingSoon(context, '数据管理'),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          
          // 关于
          _buildSectionTitle('关于'),
          Card(
            child: Column(
              children: [
                _buildItem(
                  icon: Icons.info,
                  title: '关于学了吗',
                  subtitle: '版本 1.0.0',
                  onTap: () => _showAboutDialog(context),
                ),
                const Divider(height: 1),
                _buildItem(
                  icon: Icons.help,
                  title: '帮助与反馈',
                  subtitle: '使用说明和问题反馈',
                  onTap: () => _showComingSoon(context, '帮助与反馈'),
                ),
                const Divider(height: 1),
                _buildItem(
                  icon: Icons.share,
                  title: '分享应用',
                  subtitle: '分享给朋友一起学习',
                  onTap: () => _showComingSoon(context, '分享应用'),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 退出登录按钮
          OutlinedButton.icon(
            onPressed: () => _showLogoutConfirm(context),
            icon: const Icon(Icons.exit_to_app),
            label: Text(l10n.confirm),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size(double.infinity, 48),
              foregroundColor: Colors.red,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: Colors.blue,
        ),
      ),
    );
  }
  
  Widget _buildStatItem(String title, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 20, color: Colors.blue),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
        Text(title, style: const TextStyle(fontSize: 10, color: Colors.grey)),
      ],
    );
  }
  
  Widget _buildItem({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
  
  void _showEditProfileDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('编辑个人资料'),
        content: SizedBox(
          height: 200,
          child: Column(
            children: [
              TextField(
                decoration: const InputDecoration(labelText: '用户名'),
                onChanged: (value) {
                  // 处理用户名更改
                },
              ),
              const SizedBox(height: 16),
              TextField(
                decoration: const InputDecoration(labelText: '个性签名'),
                maxLines: 3,
                onChanged: (value) {
                  // 处理签名更改
                },
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(l10n.confirm),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('个人资料已更新')),
              );
            },
            child: Text(l10n.confirm),
          ),
        ],
      ),
    );
  }
  
  void _showComingSoon(BuildContext context, String feature) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$feature 功能将在后续版本中推出')),
    );
  }
  
  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('关于学了吗'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('学了吗 - 学习任务管理与番茄专注应用'),
              const SizedBox(height: 8),
              const Text('版本: 1.0.0'),
              const SizedBox(height: 8),
              const Text('功能介绍:'),
              const SizedBox(height: 4),
              const Text('• 任务管理与提醒'),
              const Text('• 番茄钟专注计时'),
              const Text('• 错题本与复习系统'),
              const Text('• 智能定时提醒'),
              const Text('• OCR文字识别'),
              const SizedBox(height: 16),
              Text(
                '定时功能:',
                style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue),
              ),
              const SizedBox(height: 4),
              const Text('✓ 每日学习提醒'),
              const Text('✓ 任务截止提醒'),
              const Text('✓ 专注完成提醒'),
              const Text('✓ 复习计划提醒'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(l10n.confirm),
          ),
        ],
      ),
    );
  }
  
  void _showLogoutConfirm(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(l10n.confirm),
        content: const Text('确定要退出登录吗？退出后将清除本地数据。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(l10n.confirm),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('已退出登录')),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: Text(l10n.confirm),
          ),
        ],
      ),
    );
  }
}
