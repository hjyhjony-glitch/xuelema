import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'XueLeMa';

  @override
  String get features => 'Features';

  @override
  String get todayTasks => 'Today\'s Learning Tasks';

  @override
  String get viewAll => 'View All';

  @override
  String get addTask => 'Add Task';

  @override
  String get add => 'Add';

  @override
  String get taskList => 'Task List';

  @override
  String get taskDetail => 'Task Detail';

  @override
  String get taskTitle => 'Task Title';

  @override
  String get taskTitleHint => 'Enter task title';

  @override
  String get taskDescription => 'Task Description';

  @override
  String get description => 'Description';

  @override
  String get priority => 'Priority';

  @override
  String get focusDuration => 'Focus Duration';

  @override
  String get minutes => ' min';

  @override
  String get dueTime => 'Due Time';

  @override
  String get startFocus => 'Start Focus';

  @override
  String get focusMode => 'Focus';

  @override
  String get focusTime => 'Focus Time';

  @override
  String get restTime => 'Rest Time';

  @override
  String get focus => 'Focus';

  @override
  String get rest => 'Rest';

  @override
  String get startRest => 'Start Rest';

  @override
  String get completed => 'Completed';

  @override
  String get cancel => 'Cancel';

  @override
  String get save => 'Save';

  @override
  String get delete => 'Delete';

  @override
  String get ok => 'OK';

  @override
  String get overdue => 'Overdue';

  @override
  String get noTasksToday => 'No tasks today';

  @override
  String get all => 'All';

  @override
  String get today => 'Today';

  @override
  String get thisWeek => 'This Week';

  @override
  String get completedTask => 'Completed Task';

  @override
  String get searchTasks => 'Search Tasks';

  @override
  String get noTasks => 'No tasks';

  @override
  String get addFirstTask => 'Tap the button below to add your first task';

  @override
  String get subtasks => 'Subtasks';

  @override
  String get totalFocusMinutes => 'Focus Minutes';

  @override
  String get streak => 'Streak';

  @override
  String get taskStats => 'Task Statistics';

  @override
  String get createdAt => 'Created At';

  @override
  String get currentTask => 'Current Task';

  @override
  String get focusCompleted => 'Focus Complete!';

  @override
  String focusCompletedMessage(Object count) {
    return 'You have completed $count pomodoros';
  }

  @override
  String get startRestMessage => 'Time for a break!';

  @override
  String get cannotExit => 'Cannot Exit';

  @override
  String get lockWarning => 'Focus is locked. Please complete the current timer before exiting.';

  @override
  String get confirmExit => 'Confirm Exit';

  @override
  String get exitWarning => 'Timer is still running. Are you sure you want to exit?';

  @override
  String get continueTimer => 'Continue Timer';

  @override
  String get exit => 'Exit';

  @override
  String get focusLocked => 'Focus Locked';

  @override
  String get focusUnlocked => 'Focus Unlocked';

  @override
  String get focusLockedMessage => 'Focus is locked. Please complete your current task.';

  @override
  String get taskCompleted => 'Task Completed';

  @override
  String get taskOverdue => 'Task Overdue';

  @override
  String get taskInProgress => 'Task In Progress';

  @override
  String get completedAt => 'Completed At';

  @override
  String get confirmDelete => 'Confirm Delete';

  @override
  String get deleteTaskConfirm => 'Are you sure you want to delete this task? This action cannot be undone.';

  @override
  String get knowledgeBase => 'Knowledge Base';

  @override
  String get statistics => 'Statistics';

  @override
  String get settings => 'Settings';

  @override
  String get quiz => 'Quiz';

  @override
  String get quizTitle => 'Knowledge Quiz';

  @override
  String get startQuiz => 'Start Quiz';

  @override
  String get nextQuestion => 'Next';

  @override
  String get submit => 'Submit';

  @override
  String get quizResult => 'Quiz Result';

  @override
  String get correct => 'Correct';

  @override
  String get wrong => 'Wrong';

  @override
  String get score => 'Score';

  @override
  String totalQuestions(Object count) {
    return '$count Questions';
  }

  @override
  String correctAnswers(Object count) {
    return '$count Correct';
  }

  @override
  String get noQuestions => 'No questions available';

  @override
  String get mistakeBook => 'Mistake Book';

  @override
  String get mistakes => 'Mistakes';

  @override
  String get mistakeCount => 'Mistake Count';

  @override
  String get mistakeDetail => 'Mistake Detail';

  @override
  String get wrongAnswer => 'Your Answer';

  @override
  String get correctAnswer => 'Correct Answer';

  @override
  String get analysis => 'Analysis';

  @override
  String get addToMistakes => 'Add to Mistakes';

  @override
  String get removeFromMistakes => 'Remove from Mistakes';

  @override
  String get plan => 'Plan';

  @override
  String get goals => 'Goals';

  @override
  String get goalSetting => 'Goal Setting';

  @override
  String get shortTermGoal => 'Short-term Goal';

  @override
  String get longTermGoal => 'Long-term Goal';

  @override
  String get createGoal => 'Create Goal';

  @override
  String get goalTitle => 'Goal Title';

  @override
  String get goalDescription => 'Goal Description';

  @override
  String get targetDate => 'Target Date';

  @override
  String get progress => 'Progress';

  @override
  String get review => 'Review';

  @override
  String get dailyReview => 'Daily Review';

  @override
  String get weeklyReview => 'Weekly Review';

  @override
  String get monthlyReview => 'Monthly Review';

  @override
  String get createReview => 'Create Review';

  @override
  String get reviewSummary => 'Review Summary';

  @override
  String get whatWentWell => 'What Went Well';

  @override
  String get needsImprovement => 'Needs Improvement';

  @override
  String get tomorrowPlan => 'Tomorrow\'s Plan';

  @override
  String get profile => 'Profile';

  @override
  String get myInfo => 'My Info';

  @override
  String get points => 'Points';

  @override
  String get achievements => 'Achievements';

  @override
  String get learningStats => 'Learning Statistics';

  @override
  String get totalFocusTime => 'Total Focus Time';

  @override
  String get totalTasks => 'Completed Tasks';

  @override
  String get learningDays => 'Learning Days';

  @override
  String get editProfile => 'Edit Profile';

  @override
  String get notifications => 'Notifications';

  @override
  String get darkMode => 'Dark Mode';

  @override
  String get language => 'Language';

  @override
  String get about => 'About';

  @override
  String get logout => 'Logout';

  @override
  String pointsValue(Object count) {
    return '$count Points';
  }

  @override
  String hours(Object count) {
    return '$count hours';
  }

  @override
  String days(Object count) {
    return '$count days';
  }

  @override
  String get resourceLibrary => 'Resources';

  @override
  String get resources => 'Learning Resources';

  @override
  String get resourceCategories => 'Categories';

  @override
  String get download => 'Download';

  @override
  String get downloadResource => 'Download Resource';

  @override
  String get uploadResource => 'Upload Resource';

  @override
  String get upload => 'Upload';

  @override
  String get myUploads => 'My Uploads';

  @override
  String get favorites => 'Favorites';

  @override
  String get addToFavorites => 'Add to Favorites';

  @override
  String get removeFromFavorites => 'Remove from Favorites';

  @override
  String get resourceSize => 'Size';

  @override
  String get resourceType => 'Type';

  @override
  String get free => 'Free';

  @override
  String get paid => 'Paid';

  @override
  String pointsRequired(Object count) {
    return '$count Points';
  }

  @override
  String get friends => 'Friends';

  @override
  String get addFriend => 'Add Friend';

  @override
  String get searchFriend => 'Search Friends';

  @override
  String get friendRequests => 'Friend Requests';

  @override
  String get accept => 'Accept';

  @override
  String get reject => 'Reject';

  @override
  String get pending => 'Pending';

  @override
  String get confirmRemoveFriend => 'Remove Friend';

  @override
  String get removeFriendConfirm => 'Are you sure you want to remove this friend?';

  @override
  String get studyGroup => 'Study Group';

  @override
  String get groups => 'My Groups';

  @override
  String get createGroup => 'Create Group';

  @override
  String get joinGroup => 'Join Group';

  @override
  String get groupMembers => 'Members';

  @override
  String get groupName => 'Group Name';

  @override
  String get groupDescription => 'Group Description';

  @override
  String get groupOwner => 'Owner';

  @override
  String memberCount(Object count) {
    return '$count members';
  }

  @override
  String get leaveGroup => 'Leave Group';

  @override
  String get joinGroupConfirm => 'Are you sure you want to join this group?';

  @override
  String get parentMode => 'Parent Mode';

  @override
  String get childProgress => 'Child\'s Progress';

  @override
  String get viewChildTasks => 'View Child\'s Tasks';

  @override
  String get viewChildStats => 'View Statistics';

  @override
  String get dailyStudyTime => 'Today\'s Study Time';

  @override
  String get weeklyReport => 'Weekly Report';

  @override
  String get monthlyReport => 'Monthly Report';

  @override
  String get studySummary => 'Study Summary';

  @override
  String get setLimits => 'Set Limits';

  @override
  String get dailyLimit => 'Daily Study Limit';

  @override
  String get appRestrictions => 'App Restrictions';

  @override
  String get childAccount => 'Child Account';

  @override
  String get bindChild => 'Bind Child Account';

  @override
  String get unbindChild => 'Unbind';

  @override
  String get confirmUnbind => 'Confirm Unbind';

  @override
  String get unbindConfirm => 'Are you sure you want to unbind the child account?';

  @override
  String get learningStatistics => 'Learning Statistics';

  @override
  String get focusTimeStats => 'Focus Time Statistics';

  @override
  String get taskCompletionStats => 'Task Completion';

  @override
  String get studyTrend => 'Study Trend';

  @override
  String get thisMonth => 'This Month';

  @override
  String get allTime => 'All Time';

  @override
  String get averageDaily => 'Daily Average';

  @override
  String get averageFocusTime => 'Avg Focus Time';

  @override
  String get longestStreak => 'Longest Streak';

  @override
  String get completionRate => 'Completion Rate';

  @override
  String get dailyStudyChart => 'Daily Study Time';

  @override
  String get taskDistribution => 'Task Distribution';

  @override
  String get learningReport => 'Learning Report';

  @override
  String get shareReport => 'Share Report';

  @override
  String get theme => 'Theme';

  @override
  String get themeLight => 'Light';

  @override
  String get themeDark => 'Dark';

  @override
  String get themeSystem => 'System';

  @override
  String get languageSetting => 'Language';

  @override
  String get notificationsSetting => 'Notifications';

  @override
  String get focusReminders => 'Focus Reminders';

  @override
  String get taskReminders => 'Task Reminders';

  @override
  String get dailyReminder => 'Daily Study Reminder';

  @override
  String get clearCache => 'Clear Cache';

  @override
  String get cacheSize => 'Cache Size';

  @override
  String get version => 'Version';

  @override
  String get privacyPolicy => 'Privacy Policy';

  @override
  String get termsOfService => 'Terms of Service';

  @override
  String get feedback => 'Feedback';

  @override
  String get rateApp => 'Rate App';

  @override
  String get aboutUs => 'About Us';

  @override
  String get noResources => 'No resources available';

  @override
  String get noFriends => 'No friends yet';

  @override
  String get noGroups => 'No groups yet';

  @override
  String get ocrTitle => 'OCR';

  @override
  String get captureOcr => 'Capture';

  @override
  String get galleryOcr => 'Gallery';

  @override
  String get noResult => 'No recognition result';

  @override
  String get processing => 'Processing...';

  @override
  String get importTitle => 'Import';

  @override
  String get selectFile => 'Select File';

  @override
  String get importPreview => 'Import Preview';

  @override
  String get importSuccess => 'Import Successful';

  @override
  String get importError => 'Import Failed';

  @override
  String get pdfImport => 'PDF Import';

  @override
  String get selectPdf => 'Select PDF File';

  @override
  String get pdfPreview => 'PDF Preview';

  @override
  String get changeFile => 'Change File';

  @override
  String get extracting => 'Extracting...';

  @override
  String get extractionResult => 'Extraction Result';

  @override
  String get pdfType => 'PDF Type';

  @override
  String get pdfTypeText => 'Text-based PDF';

  @override
  String get pdfTypeScanned => 'Scanned PDF';

  @override
  String get pdfTypeMixed => 'Mixed PDF';

  @override
  String get questionsFound => 'Questions Found';

  @override
  String get rawTextLength => 'Raw Text Length';

  @override
  String get confidence => 'Recognition Confidence';

  @override
  String get questionsPreview => 'Questions Preview';

  @override
  String get retry => 'Retry';

  @override
  String get wrongQuestionBank => 'Wrong Questions';

  @override
  String get planning => 'Planning';

  @override
  String get import => 'Import';

  @override
  String get home => 'Home';

  @override
  String get tasks => 'Tasks';

  @override
  String get todayTasksLabel => 'Today\'s Tasks';

  @override
  String get streakDaysLabel => 'Streak Days';

  @override
  String get practice => 'Practice';

  @override
  String get noQuestionsMessage => 'No questions';

  @override
  String get noTasksMessage => 'No tasks available';

  @override
  String get profileCenter => 'Profile Center';

  @override
  String get username => 'Username';

  @override
  String get normalUser => 'Regular User';

  @override
  String get generalSettings => 'General Settings';

  @override
  String get notificationManagement => 'Notification Management';

  @override
  String get privacySecurity => 'Privacy Security';

  @override
  String get quizResults => 'Quiz Results';

  @override
  String get general => 'General';

  @override
  String get notificationSettings => 'Notification Settings';

  @override
  String get languageSettings => 'Language Settings';

  @override
  String get aboutSection => 'About';

  @override
  String get versionInfo => 'Version Info';

  @override
  String get helpCenter => 'Help Center';

  @override
  String get focusModeTitle => 'Focus Mode';

  @override
  String get pause => 'Pause';

  @override
  String get start => 'Start';

  @override
  String get reset => 'Reset';

  @override
  String get selectFileButton => 'Select File';

  @override
  String get ocrRecognition => 'OCR Recognition';

  @override
  String get chooseImageOrText => 'Choose image or enter text';

  @override
  String get takePhoto => 'Take Photo';

  @override
  String get chooseImage => 'Choose Image';

  @override
  String get paste => 'Paste';

  @override
  String get pdfImportDisabled => 'PDF Import (Temporarily Disabled)';

  @override
  String get pdfImportDisabledMessage => 'PDF import is temporarily disabled';

  @override
  String get waitingForSDKUpgrade => 'Waiting for Flutter SDK 3.7.2+';

  @override
  String get back => 'Back';

  @override
  String get taskDetails => 'Task Details';

  @override
  String get dueTimeLabel => 'Due Time:';

  @override
  String get priorityLabel => 'Priority:';

  @override
  String get startFocusButton => 'Start Focus';

  @override
  String get backButton => 'Back';

  @override
  String get continuesLearning => 'Streak';

  @override
  String get total => 'Total';

  @override
  String get highPriority => 'High Priority';

  @override
  String get completeAll => 'Complete All';

  @override
  String get goAddTask => 'Add Tasks';

  @override
  String get refresh => 'Refresh';

  @override
  String get restOrAddTask => 'Take a rest or add new tasks';

  @override
  String get addNewTask => 'Add New Task';

  @override
  String get enterTaskName => 'Enter task name';

  @override
  String get enterTaskDescription => 'Enter task description';

  @override
  String get high => 'High';

  @override
  String get medium => 'Medium';

  @override
  String get low => 'Low';

  @override
  String get close => 'Close';

  @override
  String get priorityText => 'Priority';

  @override
  String get status => 'Status';

  @override
  String get notCompleted => 'Not Completed';

  @override
  String get completedTime => 'Completed Time';

  @override
  String get reminderSettings => 'Reminder Settings';

  @override
  String get wrongQuestionBook => 'Wrong Questions';

  @override
  String get viewResults => 'View Results';

  @override
  String get goalSettings => 'Goal Settings';
}
