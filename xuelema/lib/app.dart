import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'screens/home_screen.dart';
import 'screens/task_list_screen.dart';
import 'screens/focus_screen.dart';
import 'screens/quiz_screen.dart';
import 'screens/mistake_screen.dart';
import 'screens/plan_screen.dart';
import 'screens/review_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/ocr_screen.dart';
import 'screens/import_screen.dart';
import 'screens/wrong_question_screen.dart';
import 'screens/reminder_screen.dart';
import 'screens/goal_setting_screen.dart';
import 'services/notification_service.dart';
import 'l10n/app_localizations.dart';

class XueLeMaApp extends StatefulWidget {
  const XueLeMaApp({super.key});

  @override
  State<XueLeMaApp> createState() => _XueLeMaAppState();
}

class _XueLeMaAppState extends State<XueLeMaApp> {
  final NotificationService _notificationService = NotificationService();
  
  @override
  void initState() {
    super.initState();
    _initializeServices();
  }
  
  Future<void> _initializeServices() async {
    // 初始化通知服务
    await _notificationService.init();
    
    // 设置默认提醒
    await _notificationService.setupDefaultReminders();
  }
  
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '学了吗',
      theme: ThemeData.light(),
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('zh'), // 中文
        Locale('en'), // 英文
      ],
      home: const HomeScreen(),
      routes: {
        '/tasks': (context) => const TaskListScreen(),
        '/focus': (context) => const FocusScreen(),
        '/quiz': (context) => const QuizScreen(),
        '/mistakes': (context) => const MistakeScreen(),
        '/plan': (context) => const PlanScreen(),
        '/review': (context) => const ReviewScreen(),
        '/profile': (context) => const ProfileScreen(),
        '/ocr': (context) => const OcrScreen(),
        '/import': (context) => const ImportScreen(),
        '/wrong': (context) => const WrongQuestionScreen(),
        '/reminders': (context) => const ReminderScreen(),
        '/goals': (context) => const GoalSettingScreen(),
      },
    );
  }
}
