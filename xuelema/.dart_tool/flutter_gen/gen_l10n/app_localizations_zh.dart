import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Chinese (`zh`).
class AppLocalizationsZh extends AppLocalizations {
  AppLocalizationsZh([String locale = 'zh']) : super(locale);

  @override
  String get appTitle => '学了吗';

  @override
  String get features => '功能入口';

  @override
  String get todayTasks => '今日学习任务';

  @override
  String get viewAll => '查看全部';

  @override
  String get addTask => '添加任务';

  @override
  String get add => '添加';

  @override
  String get taskList => '任务列表';

  @override
  String get taskDetail => '任务详情';

  @override
  String get taskTitle => '任务标题';

  @override
  String get taskTitleHint => '请输入任务标题';

  @override
  String get taskDescription => '任务描述';

  @override
  String get description => '描述';

  @override
  String get priority => '优先级';

  @override
  String get focusDuration => '专注时长';

  @override
  String get minutes => '分钟';

  @override
  String get dueTime => '截止时间';

  @override
  String get startFocus => '开始专注';

  @override
  String get focusMode => '专注';

  @override
  String get focusTime => '专注时间';

  @override
  String get restTime => '休息时间';

  @override
  String get focus => '专注';

  @override
  String get rest => '休息';

  @override
  String get startRest => '开始休息';

  @override
  String get completed => '已完成';

  @override
  String get cancel => '取消';

  @override
  String get save => '保存';

  @override
  String get delete => '删除';

  @override
  String get ok => '确定';

  @override
  String get confirm => '确认';

  @override
  String get overdue => '已过期';

  @override
  String get noTasksToday => '今日没有任务';

  @override
  String get all => '全部';

  @override
  String get today => '今日';

  @override
  String get thisWeek => '本周';

  @override
  String get completedTask => '已完成任务';

  @override
  String get searchTasks => '搜索任务';

  @override
  String get noTasks => '暂无任务';

  @override
  String get addFirstTask => '点击右下角添加你的第一个任务';

  @override
  String get subtasks => '子任务';

  @override
  String get totalFocusMinutes => '专注分钟';

  @override
  String get streak => '连续天数';

  @override
  String get taskStats => '任务统计';

  @override
  String get createdAt => '创建于';

  @override
  String get currentTask => '当前任务';

  @override
  String get focusCompleted => '专注完成！';

  @override
  String focusCompletedMessage(Object count) {
    return '你已经完成了 $count 个番茄钟';
  }

  @override
  String get startRestMessage => '现在休息一下吧！';

  @override
  String get cannotExit => '无法退出';

  @override
  String get lockWarning => '专注期间已锁定，请完成当前计时后再退出';

  @override
  String get confirmExit => '确认退出';

  @override
  String get exitWarning => '计时仍在进行中，确定要退出吗？';

  @override
  String get continueTimer => '继续计时';

  @override
  String get exit => '退出';

  @override
  String get focusLocked => '专注已锁定';

  @override
  String get focusUnlocked => '专注已解锁';

  @override
  String get focusLockedMessage => '专注期间已锁定，请专注完成当前任务';

  @override
  String get taskCompleted => '任务已完成';

  @override
  String get taskOverdue => '任务已过期';

  @override
  String get taskInProgress => '任务进行中';

  @override
  String get completedAt => '完成于';

  @override
  String get confirmDelete => '确认删除';

  @override
  String get deleteTaskConfirm => '确定要删除这个任务吗？此操作不可恢复。';

  @override
  String get knowledgeBase => '知识点库';

  @override
  String get statistics => '学习统计';

  @override
  String get settings => '设置';

  @override
  String get quiz => '自测';

  @override
  String get quizTitle => '知识点自测';

  @override
  String get startQuiz => '开始测试';

  @override
  String get nextQuestion => '下一题';

  @override
  String get submit => '提交';

  @override
  String get quizResult => '测试结果';

  @override
  String get correct => '正确';

  @override
  String get wrong => '错误';

  @override
  String get score => '得分';

  @override
  String totalQuestions(Object count) {
    return '共$count题';
  }

  @override
  String correctAnswers(Object count) {
    return '正确$count题';
  }

  @override
  String get noQuestions => '暂无题目';

  @override
  String get mistakeBook => '错题本';

  @override
  String get mistakes => '错题';

  @override
  String get mistakeCount => '错题数';

  @override
  String get mistakeDetail => '错题详情';

  @override
  String get wrongAnswer => '你的答案';

  @override
  String get correctAnswer => '正确答案';

  @override
  String get analysis => '解析';

  @override
  String get addToMistakes => '加入错题本';

  @override
  String get removeFromMistakes => '移出错题本';

  @override
  String get plan => '规划';

  @override
  String get goals => '目标';

  @override
  String get goalSetting => '目标设置';

  @override
  String get shortTermGoal => '短期目标';

  @override
  String get longTermGoal => '长期目标';

  @override
  String get createGoal => '创建目标';

  @override
  String get goalTitle => '目标标题';

  @override
  String get goalDescription => '目标描述';

  @override
  String get targetDate => '目标日期';

  @override
  String get progress => '进度';

  @override
  String get review => '复盘';

  @override
  String get dailyReview => '每日复盘';

  @override
  String get weeklyReview => '每周复盘';

  @override
  String get monthlyReview => '每月复盘';

  @override
  String get createReview => '创建复盘';

  @override
  String get reviewSummary => '复盘总结';

  @override
  String get whatWentWell => '做得好的';

  @override
  String get needsImprovement => '需要改进的';

  @override
  String get tomorrowPlan => '明日计划';

  @override
  String get profile => '我的';

  @override
  String get myInfo => '我的信息';

  @override
  String get points => '积分';

  @override
  String get achievements => '成就';

  @override
  String get learningStats => '学习统计';

  @override
  String get totalFocusTime => '总专注时间';

  @override
  String get totalTasks => '完成任务';

  @override
  String get learningDays => '学习天数';

  @override
  String get editProfile => '编辑资料';

  @override
  String get notifications => '通知';

  @override
  String get darkMode => '深色模式';

  @override
  String get language => '语言';

  @override
  String get about => '关于';

  @override
  String get logout => '退出登录';

  @override
  String pointsValue(Object count) {
    return '$count积分';
  }

  @override
  String hours(Object count) {
    return '$count小时';
  }

  @override
  String days(Object count) {
    return '$count天';
  }

  @override
  String get resourceLibrary => '资源库';

  @override
  String get resources => '学习资源';

  @override
  String get resourceCategories => '资源分类';

  @override
  String get download => '下载';

  @override
  String get downloadResource => '下载资源';

  @override
  String get uploadResource => '上传资源';

  @override
  String get upload => '上传';

  @override
  String get myUploads => '我的上传';

  @override
  String get favorites => '收藏';

  @override
  String get addToFavorites => '收藏';

  @override
  String get removeFromFavorites => '取消收藏';

  @override
  String get resourceSize => '资源大小';

  @override
  String get resourceType => '资源类型';

  @override
  String get free => '免费';

  @override
  String get paid => '付费';

  @override
  String pointsRequired(Object count) {
    return '需要$count积分';
  }

  @override
  String get friends => '好友';

  @override
  String get addFriend => '添加好友';

  @override
  String get searchFriend => '搜索好友';

  @override
  String get friendRequests => '好友请求';

  @override
  String get accept => '接受';

  @override
  String get reject => '拒绝';

  @override
  String get pending => '待确认';

  @override
  String get confirmRemoveFriend => '确认删除好友';

  @override
  String get removeFriendConfirm => '确定要删除这个好友吗？';

  @override
  String get studyGroup => '学习小组';

  @override
  String get groups => '我的小组';

  @override
  String get createGroup => '创建小组';

  @override
  String get joinGroup => '加入小组';

  @override
  String get groupMembers => '小组成员';

  @override
  String get groupName => '小组名称';

  @override
  String get groupDescription => '小组描述';

  @override
  String get groupOwner => '组长';

  @override
  String memberCount(Object count) {
    return '$count人';
  }

  @override
  String get leaveGroup => '退出小组';

  @override
  String get joinGroupConfirm => '确定要加入这个小组吗？';

  @override
  String get parentMode => '家长模式';

  @override
  String get childProgress => '孩子学习进度';

  @override
  String get viewChildTasks => '查看孩子任务';

  @override
  String get viewChildStats => '查看学习统计';

  @override
  String get dailyStudyTime => '今日学习时间';

  @override
  String get weeklyReport => '周报';

  @override
  String get monthlyReport => '月报';

  @override
  String get studySummary => '学习总结';

  @override
  String get setLimits => '设置限制';

  @override
  String get dailyLimit => '每日学习时长限制';

  @override
  String get appRestrictions => '应用限制';

  @override
  String get childAccount => '孩子账号';

  @override
  String get bindChild => '绑定孩子账号';

  @override
  String get unbindChild => '解除绑定';

  @override
  String get confirmUnbind => '确认解除绑定';

  @override
  String get unbindConfirm => '确定要解除与孩子账号的绑定吗？';

  @override
  String get learningStatistics => '学习数据统计';

  @override
  String get focusTimeStats => '专注时间统计';

  @override
  String get taskCompletionStats => '任务完成统计';

  @override
  String get studyTrend => '学习趋势';

  @override
  String get thisMonth => '本月';

  @override
  String get allTime => '全部时间';

  @override
  String get averageDaily => '日均';

  @override
  String get averageFocusTime => '平均专注时长';

  @override
  String get longestStreak => '最长连续';

  @override
  String get completionRate => '完成率';

  @override
  String get dailyStudyChart => '每日学习时长';

  @override
  String get taskDistribution => '任务分布';

  @override
  String get learningReport => '学习报告';

  @override
  String get shareReport => '分享报告';

  @override
  String get theme => '主题';

  @override
  String get themeLight => '浅色';

  @override
  String get themeDark => '深色';

  @override
  String get themeSystem => '跟随系统';

  @override
  String get languageSetting => '语言设置';

  @override
  String get notificationsSetting => '通知设置';

  @override
  String get focusReminders => '专注提醒';

  @override
  String get taskReminders => '任务提醒';

  @override
  String get dailyReminder => '每日学习提醒';

  @override
  String get clearCache => '清除缓存';

  @override
  String get cacheSize => '缓存大小';

  @override
  String get version => '版本';

  @override
  String get privacyPolicy => '隐私政策';

  @override
  String get termsOfService => '服务条款';

  @override
  String get feedback => '意见反馈';

  @override
  String get rateApp => '给应用评分';

  @override
  String get aboutUs => '关于我们';

  @override
  String get noResources => '暂无资源';

  @override
  String get noFriends => '暂无好友';

  @override
  String get noGroups => '暂无小组';

  @override
  String get ocrTitle => '文字识别';

  @override
  String get captureOcr => '拍照识别';

  @override
  String get galleryOcr => '相册选择';

  @override
  String get noResult => '暂无识别结果';

  @override
  String get processing => '识别中...';

  @override
  String get importTitle => '导入';

  @override
  String get selectFile => '选择文件';

  @override
  String get importPreview => '导入预览';

  @override
  String get importSuccess => '导入成功';

  @override
  String get importError => '导入失败';

  @override
  String get pdfImport => 'PDF导入';

  @override
  String get selectPdf => '选择PDF文件';

  @override
  String get pdfPreview => 'PDF预览';

  @override
  String get changeFile => '更换文件';

  @override
  String get extracting => '正在提取...';

  @override
  String get extractionResult => '提取结果';

  @override
  String get pdfType => 'PDF类型';

  @override
  String get pdfTypeText => '纯文本PDF';

  @override
  String get pdfTypeScanned => '扫描版PDF';

  @override
  String get pdfTypeMixed => '混合PDF';

  @override
  String get questionsFound => '发现题目';

  @override
  String get rawTextLength => '原始文本长度';

  @override
  String get confidence => '识别置信度';

  @override
  String get questionsPreview => '题目预览';

  @override
  String get retry => '重试';

  @override
  String get wrongQuestionBank => '错题库';

  @override
  String get planning => '规划';

  @override
  String get import => '导入';

  @override
  String get home => '首页';

  @override
  String get tasks => '任务';

  @override
  String get todayTasksLabel => '今日任务';

  @override
  String get streakDaysLabel => '连续天数';

  @override
  String get practice => '练习';

  @override
  String get noQuestionsMessage => '没有题目';

  @override
  String get noTasksMessage => '暂无任务';

  @override
  String get profileCenter => '个人中心';

  @override
  String get username => '用户名';

  @override
  String get normalUser => '普通用户';

  @override
  String get generalSettings => '通用设置';

  @override
  String get notificationManagement => '通知管理';

  @override
  String get privacySecurity => '隐私安全';

  @override
  String get quizResults => '测验结果';

  @override
  String get general => '通用';

  @override
  String get notificationSettings => '通知设置';

  @override
  String get languageSettings => '语言设置';

  @override
  String get aboutSection => '关于';

  @override
  String get versionInfo => '版本信息';

  @override
  String get helpCenter => '帮助中心';

  @override
  String get focusModeTitle => '专注模式';

  @override
  String get pause => '暂停';

  @override
  String get start => '开始';

  @override
  String get reset => '重置';

  @override
  String get selectFileButton => '选择文件';

  @override
  String get ocrRecognition => 'OCR识别';

  @override
  String get chooseImageOrText => '请选择图片或输入文字';

  @override
  String get takePhoto => '拍照';

  @override
  String get chooseImage => '选择图片';

  @override
  String get paste => '粘贴';

  @override
  String get pdfImportDisabled => 'PDF导入（暂时禁用）';

  @override
  String get pdfImportDisabledMessage => 'PDF导入功能暂时禁用';

  @override
  String get waitingForSDKUpgrade => '等待Flutter SDK升级到3.7.2+';

  @override
  String get back => '返回';

  @override
  String get taskDetails => '任务详情';

  @override
  String get dueTimeLabel => '截止时间:';

  @override
  String get priorityLabel => '优先级:';

  @override
  String get startFocusButton => '开始专注';

  @override
  String get backButton => '返回';

  @override
  String get continuesLearning => '连续学习';

  @override
  String get total => '总计';

  @override
  String get highPriority => '高优先级';

  @override
  String get completeAll => '一键完成';

  @override
  String get goAddTask => '去添加任务';

  @override
  String get refresh => '刷新';

  @override
  String get restOrAddTask => '休息一下或添加新任务';

  @override
  String get addNewTask => '添加新任务';

  @override
  String get enterTaskName => '输入任务名称';

  @override
  String get enterTaskDescription => '输入任务描述';

  @override
  String get high => '高';

  @override
  String get medium => '中';

  @override
  String get low => '低';

  @override
  String get close => '关闭';

  @override
  String get priorityText => '优先级';

  @override
  String get status => '状态';

  @override
  String get notCompleted => '未完成';

  @override
  String get completedTime => '完成时间';

  @override
  String get reminderSettings => '提醒设置';

  @override
  String get wrongQuestionBook => '错题本';

  @override
  String get viewResults => '查看结果';

  @override
  String get goalSettings => '目标设置';
}
