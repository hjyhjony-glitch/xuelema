/// 资源详情页面（简化版）
import 'package:flutter/material.dart';

class ResourceDetailScreen extends StatefulWidget {
  const ResourceDetailScreen({super.key});

  @override
  State<ResourceDetailScreen> createState() => _ResourceDetailScreenState();
}

class _ResourceDetailScreenState extends State<ResourceDetailScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('资源详情')),
      body: const Center(child: Text('资源详情')),
    );
  }
}
