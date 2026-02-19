import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_zh.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'gen_l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale) : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates = <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('zh')
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'XueLeMa'**
  String get appTitle;

  /// No description provided for @features.
  ///
  /// In en, this message translates to:
  /// **'Features'**
  String get features;

  /// No description provided for @todayTasks.
  ///
  /// In en, this message translates to:
  /// **'Today\'s Learning Tasks'**
  String get todayTasks;

  /// No description provided for @viewAll.
  ///
  /// In en, this message translates to:
  /// **'View All'**
  String get viewAll;

  /// No description provided for @addTask.
  ///
  /// In en, this message translates to:
  /// **'Add Task'**
  String get addTask;

  /// No description provided for @add.
  ///
  /// In en, this message translates to:
  /// **'Add'**
  String get add;

  /// No description provided for @taskList.
  ///
  /// In en, this message translates to:
  /// **'Task List'**
  String get taskList;

  /// No description provided for @taskDetail.
  ///
  /// In en, this message translates to:
  /// **'Task Detail'**
  String get taskDetail;

  /// No description provided for @taskTitle.
  ///
  /// In en, this message translates to:
  /// **'Task Title'**
  String get taskTitle;

  /// No description provided for @taskTitleHint.
  ///
  /// In en, this message translates to:
  /// **'Enter task title'**
  String get taskTitleHint;

  /// No description provided for @taskDescription.
  ///
  /// In en, this message translates to:
  /// **'Task Description'**
  String get taskDescription;

  /// No description provided for @description.
  ///
  /// In en, this message translates to:
  /// **'Description'**
  String get description;

  /// No description provided for @priority.
  ///
  /// In en, this message translates to:
  /// **'Priority'**
  String get priority;

  /// No description provided for @focusDuration.
  ///
  /// In en, this message translates to:
  /// **'Focus Duration'**
  String get focusDuration;

  /// No description provided for @minutes.
  ///
  /// In en, this message translates to:
  /// **' min'**
  String get minutes;

  /// No description provided for @dueTime.
  ///
  /// In en, this message translates to:
  /// **'Due Time'**
  String get dueTime;

  /// No description provided for @startFocus.
  ///
  /// In en, this message translates to:
  /// **'Start Focus'**
  String get startFocus;

  /// No description provided for @focusMode.
  ///
  /// In en, this message translates to:
  /// **'Focus'**
  String get focusMode;

  /// No description provided for @focusTime.
  ///
  /// In en, this message translates to:
  /// **'Focus Time'**
  String get focusTime;

  /// No description provided for @restTime.
  ///
  /// In en, this message translates to:
  /// **'Rest Time'**
  String get restTime;

  /// No description provided for @focus.
  ///
  /// In en, this message translates to:
  /// **'Focus'**
  String get focus;

  /// No description provided for @rest.
  ///
  /// In en, this message translates to:
  /// **'Rest'**
  String get rest;

  /// No description provided for @startRest.
  ///
  /// In en, this message translates to:
  /// **'Start Rest'**
  String get startRest;

  /// No description provided for @completed.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get completed;

  /// No description provided for @cancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// No description provided for @save.
  ///
  /// In en, this message translates to:
  /// **'Save'**
  String get save;

  /// No description provided for @delete.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get delete;

  /// No description provided for @ok.
  ///
  /// In en, this message translates to:
  /// **'OK'**
  String get ok;

  /// No description provided for @confirm.
  ///
  /// In en, this message translates to:
  /// **'Confirm'**
  String get confirm;

  /// No description provided for @overdue.
  ///
  /// In en, this message translates to:
  /// **'Overdue'**
  String get overdue;

  /// No description provided for @noTasksToday.
  ///
  /// In en, this message translates to:
  /// **'No tasks today'**
  String get noTasksToday;

  /// No description provided for @all.
  ///
  /// In en, this message translates to:
  /// **'All'**
  String get all;

  /// No description provided for @today.
  ///
  /// In en, this message translates to:
  /// **'Today'**
  String get today;

  /// No description provided for @thisWeek.
  ///
  /// In en, this message translates to:
  /// **'This Week'**
  String get thisWeek;

  /// No description provided for @completedTask.
  ///
  /// In en, this message translates to:
  /// **'Completed Task'**
  String get completedTask;

  /// No description provided for @searchTasks.
  ///
  /// In en, this message translates to:
  /// **'Search Tasks'**
  String get searchTasks;

  /// No description provided for @noTasks.
  ///
  /// In en, this message translates to:
  /// **'No tasks'**
  String get noTasks;

  /// No description provided for @addFirstTask.
  ///
  /// In en, this message translates to:
  /// **'Tap the button below to add your first task'**
  String get addFirstTask;

  /// No description provided for @subtasks.
  ///
  /// In en, this message translates to:
  /// **'Subtasks'**
  String get subtasks;

  /// No description provided for @totalFocusMinutes.
  ///
  /// In en, this message translates to:
  /// **'Focus Minutes'**
  String get totalFocusMinutes;

  /// No description provided for @streak.
  ///
  /// In en, this message translates to:
  /// **'Streak'**
  String get streak;

  /// No description provided for @taskStats.
  ///
  /// In en, this message translates to:
  /// **'Task Statistics'**
  String get taskStats;

  /// No description provided for @createdAt.
  ///
  /// In en, this message translates to:
  /// **'Created At'**
  String get createdAt;

  /// No description provided for @currentTask.
  ///
  /// In en, this message translates to:
  /// **'Current Task'**
  String get currentTask;

  /// No description provided for @focusCompleted.
  ///
  /// In en, this message translates to:
  /// **'Focus Complete!'**
  String get focusCompleted;

  /// No description provided for @focusCompletedMessage.
  ///
  /// In en, this message translates to:
  /// **'You have completed {count} pomodoros'**
  String focusCompletedMessage(Object count);

  /// No description provided for @startRestMessage.
  ///
  /// In en, this message translates to:
  /// **'Time for a break!'**
  String get startRestMessage;

  /// No description provided for @cannotExit.
  ///
  /// In en, this message translates to:
  /// **'Cannot Exit'**
  String get cannotExit;

  /// No description provided for @lockWarning.
  ///
  /// In en, this message translates to:
  /// **'Focus is locked. Please complete the current timer before exiting.'**
  String get lockWarning;

  /// No description provided for @confirmExit.
  ///
  /// In en, this message translates to:
  /// **'Confirm Exit'**
  String get confirmExit;

  /// No description provided for @exitWarning.
  ///
  /// In en, this message translates to:
  /// **'Timer is still running. Are you sure you want to exit?'**
  String get exitWarning;

  /// No description provided for @continueTimer.
  ///
  /// In en, this message translates to:
  /// **'Continue Timer'**
  String get continueTimer;

  /// No description provided for @exit.
  ///
  /// In en, this message translates to:
  /// **'Exit'**
  String get exit;

  /// No description provided for @focusLocked.
  ///
  /// In en, this message translates to:
  /// **'Focus Locked'**
  String get focusLocked;

  /// No description provided for @focusUnlocked.
  ///
  /// In en, this message translates to:
  /// **'Focus Unlocked'**
  String get focusUnlocked;

  /// No description provided for @focusLockedMessage.
  ///
  /// In en, this message translates to:
  /// **'Focus is locked. Please complete your current task.'**
  String get focusLockedMessage;

  /// No description provided for @taskCompleted.
  ///
  /// In en, this message translates to:
  /// **'Task Completed'**
  String get taskCompleted;

  /// No description provided for @taskOverdue.
  ///
  /// In en, this message translates to:
  /// **'Task Overdue'**
  String get taskOverdue;

  /// No description provided for @taskInProgress.
  ///
  /// In en, this message translates to:
  /// **'Task In Progress'**
  String get taskInProgress;

  /// No description provided for @completedAt.
  ///
  /// In en, this message translates to:
  /// **'Completed At'**
  String get completedAt;

  /// No description provided for @confirmDelete.
  ///
  /// In en, this message translates to:
  /// **'Confirm Delete'**
  String get confirmDelete;

  /// No description provided for @deleteTaskConfirm.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete this task? This action cannot be undone.'**
  String get deleteTaskConfirm;

  /// No description provided for @knowledgeBase.
  ///
  /// In en, this message translates to:
  /// **'Knowledge Base'**
  String get knowledgeBase;

  /// No description provided for @statistics.
  ///
  /// In en, this message translates to:
  /// **'Statistics'**
  String get statistics;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @quiz.
  ///
  /// In en, this message translates to:
  /// **'Quiz'**
  String get quiz;

  /// No description provided for @quizTitle.
  ///
  /// In en, this message translates to:
  /// **'Knowledge Quiz'**
  String get quizTitle;

  /// No description provided for @startQuiz.
  ///
  /// In en, this message translates to:
  /// **'Start Quiz'**
  String get startQuiz;

  /// No description provided for @nextQuestion.
  ///
  /// In en, this message translates to:
  /// **'Next'**
  String get nextQuestion;

  /// No description provided for @submit.
  ///
  /// In en, this message translates to:
  /// **'Submit'**
  String get submit;

  /// No description provided for @quizResult.
  ///
  /// In en, this message translates to:
  /// **'Quiz Result'**
  String get quizResult;

  /// No description provided for @correct.
  ///
  /// In en, this message translates to:
  /// **'Correct'**
  String get correct;

  /// No description provided for @wrong.
  ///
  /// In en, this message translates to:
  /// **'Wrong'**
  String get wrong;

  /// No description provided for @score.
  ///
  /// In en, this message translates to:
  /// **'Score'**
  String get score;

  /// No description provided for @totalQuestions.
  ///
  /// In en, this message translates to:
  /// **'{count} Questions'**
  String totalQuestions(Object count);

  /// No description provided for @correctAnswers.
  ///
  /// In en, this message translates to:
  /// **'{count} Correct'**
  String correctAnswers(Object count);

  /// No description provided for @noQuestions.
  ///
  /// In en, this message translates to:
  /// **'No questions available'**
  String get noQuestions;

  /// No description provided for @mistakeBook.
  ///
  /// In en, this message translates to:
  /// **'Mistake Book'**
  String get mistakeBook;

  /// No description provided for @mistakes.
  ///
  /// In en, this message translates to:
  /// **'Mistakes'**
  String get mistakes;

  /// No description provided for @mistakeCount.
  ///
  /// In en, this message translates to:
  /// **'Mistake Count'**
  String get mistakeCount;

  /// No description provided for @mistakeDetail.
  ///
  /// In en, this message translates to:
  /// **'Mistake Detail'**
  String get mistakeDetail;

  /// No description provided for @wrongAnswer.
  ///
  /// In en, this message translates to:
  /// **'Your Answer'**
  String get wrongAnswer;

  /// No description provided for @correctAnswer.
  ///
  /// In en, this message translates to:
  /// **'Correct Answer'**
  String get correctAnswer;

  /// No description provided for @analysis.
  ///
  /// In en, this message translates to:
  /// **'Analysis'**
  String get analysis;

  /// No description provided for @addToMistakes.
  ///
  /// In en, this message translates to:
  /// **'Add to Mistakes'**
  String get addToMistakes;

  /// No description provided for @removeFromMistakes.
  ///
  /// In en, this message translates to:
  /// **'Remove from Mistakes'**
  String get removeFromMistakes;

  /// No description provided for @plan.
  ///
  /// In en, this message translates to:
  /// **'Plan'**
  String get plan;

  /// No description provided for @goals.
  ///
  /// In en, this message translates to:
  /// **'Goals'**
  String get goals;

  /// No description provided for @goalSetting.
  ///
  /// In en, this message translates to:
  /// **'Goal Setting'**
  String get goalSetting;

  /// No description provided for @shortTermGoal.
  ///
  /// In en, this message translates to:
  /// **'Short-term Goal'**
  String get shortTermGoal;

  /// No description provided for @longTermGoal.
  ///
  /// In en, this message translates to:
  /// **'Long-term Goal'**
  String get longTermGoal;

  /// No description provided for @createGoal.
  ///
  /// In en, this message translates to:
  /// **'Create Goal'**
  String get createGoal;

  /// No description provided for @goalTitle.
  ///
  /// In en, this message translates to:
  /// **'Goal Title'**
  String get goalTitle;

  /// No description provided for @goalDescription.
  ///
  /// In en, this message translates to:
  /// **'Goal Description'**
  String get goalDescription;

  /// No description provided for @targetDate.
  ///
  /// In en, this message translates to:
  /// **'Target Date'**
  String get targetDate;

  /// No description provided for @progress.
  ///
  /// In en, this message translates to:
  /// **'Progress'**
  String get progress;

  /// No description provided for @review.
  ///
  /// In en, this message translates to:
  /// **'Review'**
  String get review;

  /// No description provided for @dailyReview.
  ///
  /// In en, this message translates to:
  /// **'Daily Review'**
  String get dailyReview;

  /// No description provided for @weeklyReview.
  ///
  /// In en, this message translates to:
  /// **'Weekly Review'**
  String get weeklyReview;

  /// No description provided for @monthlyReview.
  ///
  /// In en, this message translates to:
  /// **'Monthly Review'**
  String get monthlyReview;

  /// No description provided for @createReview.
  ///
  /// In en, this message translates to:
  /// **'Create Review'**
  String get createReview;

  /// No description provided for @reviewSummary.
  ///
  /// In en, this message translates to:
  /// **'Review Summary'**
  String get reviewSummary;

  /// No description provided for @whatWentWell.
  ///
  /// In en, this message translates to:
  /// **'What Went Well'**
  String get whatWentWell;

  /// No description provided for @needsImprovement.
  ///
  /// In en, this message translates to:
  /// **'Needs Improvement'**
  String get needsImprovement;

  /// No description provided for @tomorrowPlan.
  ///
  /// In en, this message translates to:
  /// **'Tomorrow\'s Plan'**
  String get tomorrowPlan;

  /// No description provided for @profile.
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get profile;

  /// No description provided for @myInfo.
  ///
  /// In en, this message translates to:
  /// **'My Info'**
  String get myInfo;

  /// No description provided for @points.
  ///
  /// In en, this message translates to:
  /// **'Points'**
  String get points;

  /// No description provided for @achievements.
  ///
  /// In en, this message translates to:
  /// **'Achievements'**
  String get achievements;

  /// No description provided for @learningStats.
  ///
  /// In en, this message translates to:
  /// **'Learning Statistics'**
  String get learningStats;

  /// No description provided for @totalFocusTime.
  ///
  /// In en, this message translates to:
  /// **'Total Focus Time'**
  String get totalFocusTime;

  /// No description provided for @totalTasks.
  ///
  /// In en, this message translates to:
  /// **'Completed Tasks'**
  String get totalTasks;

  /// No description provided for @learningDays.
  ///
  /// In en, this message translates to:
  /// **'Learning Days'**
  String get learningDays;

  /// No description provided for @editProfile.
  ///
  /// In en, this message translates to:
  /// **'Edit Profile'**
  String get editProfile;

  /// No description provided for @notifications.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get notifications;

  /// No description provided for @darkMode.
  ///
  /// In en, this message translates to:
  /// **'Dark Mode'**
  String get darkMode;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @about.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get about;

  /// No description provided for @logout.
  ///
  /// In en, this message translates to:
  /// **'Logout'**
  String get logout;

  /// No description provided for @pointsValue.
  ///
  /// In en, this message translates to:
  /// **'{count} Points'**
  String pointsValue(Object count);

  /// No description provided for @hours.
  ///
  /// In en, this message translates to:
  /// **'{count} hours'**
  String hours(Object count);

  /// No description provided for @days.
  ///
  /// In en, this message translates to:
  /// **'{count} days'**
  String days(Object count);

  /// No description provided for @resourceLibrary.
  ///
  /// In en, this message translates to:
  /// **'Resources'**
  String get resourceLibrary;

  /// No description provided for @resources.
  ///
  /// In en, this message translates to:
  /// **'Learning Resources'**
  String get resources;

  /// No description provided for @resourceCategories.
  ///
  /// In en, this message translates to:
  /// **'Categories'**
  String get resourceCategories;

  /// No description provided for @download.
  ///
  /// In en, this message translates to:
  /// **'Download'**
  String get download;

  /// No description provided for @downloadResource.
  ///
  /// In en, this message translates to:
  /// **'Download Resource'**
  String get downloadResource;

  /// No description provided for @uploadResource.
  ///
  /// In en, this message translates to:
  /// **'Upload Resource'**
  String get uploadResource;

  /// No description provided for @upload.
  ///
  /// In en, this message translates to:
  /// **'Upload'**
  String get upload;

  /// No description provided for @myUploads.
  ///
  /// In en, this message translates to:
  /// **'My Uploads'**
  String get myUploads;

  /// No description provided for @favorites.
  ///
  /// In en, this message translates to:
  /// **'Favorites'**
  String get favorites;

  /// No description provided for @addToFavorites.
  ///
  /// In en, this message translates to:
  /// **'Add to Favorites'**
  String get addToFavorites;

  /// No description provided for @removeFromFavorites.
  ///
  /// In en, this message translates to:
  /// **'Remove from Favorites'**
  String get removeFromFavorites;

  /// No description provided for @resourceSize.
  ///
  /// In en, this message translates to:
  /// **'Size'**
  String get resourceSize;

  /// No description provided for @resourceType.
  ///
  /// In en, this message translates to:
  /// **'Type'**
  String get resourceType;

  /// No description provided for @free.
  ///
  /// In en, this message translates to:
  /// **'Free'**
  String get free;

  /// No description provided for @paid.
  ///
  /// In en, this message translates to:
  /// **'Paid'**
  String get paid;

  /// No description provided for @pointsRequired.
  ///
  /// In en, this message translates to:
  /// **'{count} Points'**
  String pointsRequired(Object count);

  /// No description provided for @friends.
  ///
  /// In en, this message translates to:
  /// **'Friends'**
  String get friends;

  /// No description provided for @addFriend.
  ///
  /// In en, this message translates to:
  /// **'Add Friend'**
  String get addFriend;

  /// No description provided for @searchFriend.
  ///
  /// In en, this message translates to:
  /// **'Search Friends'**
  String get searchFriend;

  /// No description provided for @friendRequests.
  ///
  /// In en, this message translates to:
  /// **'Friend Requests'**
  String get friendRequests;

  /// No description provided for @accept.
  ///
  /// In en, this message translates to:
  /// **'Accept'**
  String get accept;

  /// No description provided for @reject.
  ///
  /// In en, this message translates to:
  /// **'Reject'**
  String get reject;

  /// No description provided for @pending.
  ///
  /// In en, this message translates to:
  /// **'Pending'**
  String get pending;

  /// No description provided for @confirmRemoveFriend.
  ///
  /// In en, this message translates to:
  /// **'Remove Friend'**
  String get confirmRemoveFriend;

  /// No description provided for @removeFriendConfirm.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to remove this friend?'**
  String get removeFriendConfirm;

  /// No description provided for @studyGroup.
  ///
  /// In en, this message translates to:
  /// **'Study Group'**
  String get studyGroup;

  /// No description provided for @groups.
  ///
  /// In en, this message translates to:
  /// **'My Groups'**
  String get groups;

  /// No description provided for @createGroup.
  ///
  /// In en, this message translates to:
  /// **'Create Group'**
  String get createGroup;

  /// No description provided for @joinGroup.
  ///
  /// In en, this message translates to:
  /// **'Join Group'**
  String get joinGroup;

  /// No description provided for @groupMembers.
  ///
  /// In en, this message translates to:
  /// **'Members'**
  String get groupMembers;

  /// No description provided for @groupName.
  ///
  /// In en, this message translates to:
  /// **'Group Name'**
  String get groupName;

  /// No description provided for @groupDescription.
  ///
  /// In en, this message translates to:
  /// **'Group Description'**
  String get groupDescription;

  /// No description provided for @groupOwner.
  ///
  /// In en, this message translates to:
  /// **'Owner'**
  String get groupOwner;

  /// No description provided for @memberCount.
  ///
  /// In en, this message translates to:
  /// **'{count} members'**
  String memberCount(Object count);

  /// No description provided for @leaveGroup.
  ///
  /// In en, this message translates to:
  /// **'Leave Group'**
  String get leaveGroup;

  /// No description provided for @joinGroupConfirm.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to join this group?'**
  String get joinGroupConfirm;

  /// No description provided for @parentMode.
  ///
  /// In en, this message translates to:
  /// **'Parent Mode'**
  String get parentMode;

  /// No description provided for @childProgress.
  ///
  /// In en, this message translates to:
  /// **'Child\'s Progress'**
  String get childProgress;

  /// No description provided for @viewChildTasks.
  ///
  /// In en, this message translates to:
  /// **'View Child\'s Tasks'**
  String get viewChildTasks;

  /// No description provided for @viewChildStats.
  ///
  /// In en, this message translates to:
  /// **'View Statistics'**
  String get viewChildStats;

  /// No description provided for @dailyStudyTime.
  ///
  /// In en, this message translates to:
  /// **'Today\'s Study Time'**
  String get dailyStudyTime;

  /// No description provided for @weeklyReport.
  ///
  /// In en, this message translates to:
  /// **'Weekly Report'**
  String get weeklyReport;

  /// No description provided for @monthlyReport.
  ///
  /// In en, this message translates to:
  /// **'Monthly Report'**
  String get monthlyReport;

  /// No description provided for @studySummary.
  ///
  /// In en, this message translates to:
  /// **'Study Summary'**
  String get studySummary;

  /// No description provided for @setLimits.
  ///
  /// In en, this message translates to:
  /// **'Set Limits'**
  String get setLimits;

  /// No description provided for @dailyLimit.
  ///
  /// In en, this message translates to:
  /// **'Daily Study Limit'**
  String get dailyLimit;

  /// No description provided for @appRestrictions.
  ///
  /// In en, this message translates to:
  /// **'App Restrictions'**
  String get appRestrictions;

  /// No description provided for @childAccount.
  ///
  /// In en, this message translates to:
  /// **'Child Account'**
  String get childAccount;

  /// No description provided for @bindChild.
  ///
  /// In en, this message translates to:
  /// **'Bind Child Account'**
  String get bindChild;

  /// No description provided for @unbindChild.
  ///
  /// In en, this message translates to:
  /// **'Unbind'**
  String get unbindChild;

  /// No description provided for @confirmUnbind.
  ///
  /// In en, this message translates to:
  /// **'Confirm Unbind'**
  String get confirmUnbind;

  /// No description provided for @unbindConfirm.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to unbind the child account?'**
  String get unbindConfirm;

  /// No description provided for @learningStatistics.
  ///
  /// In en, this message translates to:
  /// **'Learning Statistics'**
  String get learningStatistics;

  /// No description provided for @focusTimeStats.
  ///
  /// In en, this message translates to:
  /// **'Focus Time Statistics'**
  String get focusTimeStats;

  /// No description provided for @taskCompletionStats.
  ///
  /// In en, this message translates to:
  /// **'Task Completion'**
  String get taskCompletionStats;

  /// No description provided for @studyTrend.
  ///
  /// In en, this message translates to:
  /// **'Study Trend'**
  String get studyTrend;

  /// No description provided for @thisMonth.
  ///
  /// In en, this message translates to:
  /// **'This Month'**
  String get thisMonth;

  /// No description provided for @allTime.
  ///
  /// In en, this message translates to:
  /// **'All Time'**
  String get allTime;

  /// No description provided for @averageDaily.
  ///
  /// In en, this message translates to:
  /// **'Daily Average'**
  String get averageDaily;

  /// No description provided for @averageFocusTime.
  ///
  /// In en, this message translates to:
  /// **'Avg Focus Time'**
  String get averageFocusTime;

  /// No description provided for @longestStreak.
  ///
  /// In en, this message translates to:
  /// **'Longest Streak'**
  String get longestStreak;

  /// No description provided for @completionRate.
  ///
  /// In en, this message translates to:
  /// **'Completion Rate'**
  String get completionRate;

  /// No description provided for @dailyStudyChart.
  ///
  /// In en, this message translates to:
  /// **'Daily Study Time'**
  String get dailyStudyChart;

  /// No description provided for @taskDistribution.
  ///
  /// In en, this message translates to:
  /// **'Task Distribution'**
  String get taskDistribution;

  /// No description provided for @learningReport.
  ///
  /// In en, this message translates to:
  /// **'Learning Report'**
  String get learningReport;

  /// No description provided for @shareReport.
  ///
  /// In en, this message translates to:
  /// **'Share Report'**
  String get shareReport;

  /// No description provided for @theme.
  ///
  /// In en, this message translates to:
  /// **'Theme'**
  String get theme;

  /// No description provided for @themeLight.
  ///
  /// In en, this message translates to:
  /// **'Light'**
  String get themeLight;

  /// No description provided for @themeDark.
  ///
  /// In en, this message translates to:
  /// **'Dark'**
  String get themeDark;

  /// No description provided for @themeSystem.
  ///
  /// In en, this message translates to:
  /// **'System'**
  String get themeSystem;

  /// No description provided for @languageSetting.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get languageSetting;

  /// No description provided for @notificationsSetting.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get notificationsSetting;

  /// No description provided for @focusReminders.
  ///
  /// In en, this message translates to:
  /// **'Focus Reminders'**
  String get focusReminders;

  /// No description provided for @taskReminders.
  ///
  /// In en, this message translates to:
  /// **'Task Reminders'**
  String get taskReminders;

  /// No description provided for @dailyReminder.
  ///
  /// In en, this message translates to:
  /// **'Daily Study Reminder'**
  String get dailyReminder;

  /// No description provided for @clearCache.
  ///
  /// In en, this message translates to:
  /// **'Clear Cache'**
  String get clearCache;

  /// No description provided for @cacheSize.
  ///
  /// In en, this message translates to:
  /// **'Cache Size'**
  String get cacheSize;

  /// No description provided for @version.
  ///
  /// In en, this message translates to:
  /// **'Version'**
  String get version;

  /// No description provided for @privacyPolicy.
  ///
  /// In en, this message translates to:
  /// **'Privacy Policy'**
  String get privacyPolicy;

  /// No description provided for @termsOfService.
  ///
  /// In en, this message translates to:
  /// **'Terms of Service'**
  String get termsOfService;

  /// No description provided for @feedback.
  ///
  /// In en, this message translates to:
  /// **'Feedback'**
  String get feedback;

  /// No description provided for @rateApp.
  ///
  /// In en, this message translates to:
  /// **'Rate App'**
  String get rateApp;

  /// No description provided for @aboutUs.
  ///
  /// In en, this message translates to:
  /// **'About Us'**
  String get aboutUs;

  /// No description provided for @noResources.
  ///
  /// In en, this message translates to:
  /// **'No resources available'**
  String get noResources;

  /// No description provided for @noFriends.
  ///
  /// In en, this message translates to:
  /// **'No friends yet'**
  String get noFriends;

  /// No description provided for @noGroups.
  ///
  /// In en, this message translates to:
  /// **'No groups yet'**
  String get noGroups;

  /// No description provided for @ocrTitle.
  ///
  /// In en, this message translates to:
  /// **'OCR'**
  String get ocrTitle;

  /// No description provided for @captureOcr.
  ///
  /// In en, this message translates to:
  /// **'Capture'**
  String get captureOcr;

  /// No description provided for @galleryOcr.
  ///
  /// In en, this message translates to:
  /// **'Gallery'**
  String get galleryOcr;

  /// No description provided for @noResult.
  ///
  /// In en, this message translates to:
  /// **'No recognition result'**
  String get noResult;

  /// No description provided for @processing.
  ///
  /// In en, this message translates to:
  /// **'Processing...'**
  String get processing;

  /// No description provided for @importTitle.
  ///
  /// In en, this message translates to:
  /// **'Import'**
  String get importTitle;

  /// No description provided for @selectFile.
  ///
  /// In en, this message translates to:
  /// **'Select File'**
  String get selectFile;

  /// No description provided for @importPreview.
  ///
  /// In en, this message translates to:
  /// **'Import Preview'**
  String get importPreview;

  /// No description provided for @importSuccess.
  ///
  /// In en, this message translates to:
  /// **'Import Successful'**
  String get importSuccess;

  /// No description provided for @importError.
  ///
  /// In en, this message translates to:
  /// **'Import Failed'**
  String get importError;

  /// No description provided for @pdfImport.
  ///
  /// In en, this message translates to:
  /// **'PDF Import'**
  String get pdfImport;

  /// No description provided for @selectPdf.
  ///
  /// In en, this message translates to:
  /// **'Select PDF File'**
  String get selectPdf;

  /// No description provided for @pdfPreview.
  ///
  /// In en, this message translates to:
  /// **'PDF Preview'**
  String get pdfPreview;

  /// No description provided for @changeFile.
  ///
  /// In en, this message translates to:
  /// **'Change File'**
  String get changeFile;

  /// No description provided for @extracting.
  ///
  /// In en, this message translates to:
  /// **'Extracting...'**
  String get extracting;

  /// No description provided for @extractionResult.
  ///
  /// In en, this message translates to:
  /// **'Extraction Result'**
  String get extractionResult;

  /// No description provided for @pdfType.
  ///
  /// In en, this message translates to:
  /// **'PDF Type'**
  String get pdfType;

  /// No description provided for @pdfTypeText.
  ///
  /// In en, this message translates to:
  /// **'Text-based PDF'**
  String get pdfTypeText;

  /// No description provided for @pdfTypeScanned.
  ///
  /// In en, this message translates to:
  /// **'Scanned PDF'**
  String get pdfTypeScanned;

  /// No description provided for @pdfTypeMixed.
  ///
  /// In en, this message translates to:
  /// **'Mixed PDF'**
  String get pdfTypeMixed;

  /// No description provided for @questionsFound.
  ///
  /// In en, this message translates to:
  /// **'Questions Found'**
  String get questionsFound;

  /// No description provided for @rawTextLength.
  ///
  /// In en, this message translates to:
  /// **'Raw Text Length'**
  String get rawTextLength;

  /// No description provided for @confidence.
  ///
  /// In en, this message translates to:
  /// **'Recognition Confidence'**
  String get confidence;

  /// No description provided for @questionsPreview.
  ///
  /// In en, this message translates to:
  /// **'Questions Preview'**
  String get questionsPreview;

  /// No description provided for @retry.
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;

  /// No description provided for @wrongQuestionBank.
  ///
  /// In en, this message translates to:
  /// **'Wrong Questions'**
  String get wrongQuestionBank;

  /// No description provided for @planning.
  ///
  /// In en, this message translates to:
  /// **'Planning'**
  String get planning;

  /// No description provided for @import.
  ///
  /// In en, this message translates to:
  /// **'Import'**
  String get import;

  /// No description provided for @home.
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get home;

  /// No description provided for @tasks.
  ///
  /// In en, this message translates to:
  /// **'Tasks'**
  String get tasks;

  /// No description provided for @todayTasksLabel.
  ///
  /// In en, this message translates to:
  /// **'Today\'s Tasks'**
  String get todayTasksLabel;

  /// No description provided for @streakDaysLabel.
  ///
  /// In en, this message translates to:
  /// **'Streak Days'**
  String get streakDaysLabel;

  /// No description provided for @practice.
  ///
  /// In en, this message translates to:
  /// **'Practice'**
  String get practice;

  /// No description provided for @noQuestionsMessage.
  ///
  /// In en, this message translates to:
  /// **'No questions'**
  String get noQuestionsMessage;

  /// No description provided for @noTasksMessage.
  ///
  /// In en, this message translates to:
  /// **'No tasks available'**
  String get noTasksMessage;

  /// No description provided for @profileCenter.
  ///
  /// In en, this message translates to:
  /// **'Profile Center'**
  String get profileCenter;

  /// No description provided for @username.
  ///
  /// In en, this message translates to:
  /// **'Username'**
  String get username;

  /// No description provided for @normalUser.
  ///
  /// In en, this message translates to:
  /// **'Regular User'**
  String get normalUser;

  /// No description provided for @generalSettings.
  ///
  /// In en, this message translates to:
  /// **'General Settings'**
  String get generalSettings;

  /// No description provided for @notificationManagement.
  ///
  /// In en, this message translates to:
  /// **'Notification Management'**
  String get notificationManagement;

  /// No description provided for @privacySecurity.
  ///
  /// In en, this message translates to:
  /// **'Privacy Security'**
  String get privacySecurity;

  /// No description provided for @quizResults.
  ///
  /// In en, this message translates to:
  /// **'Quiz Results'**
  String get quizResults;

  /// No description provided for @general.
  ///
  /// In en, this message translates to:
  /// **'General'**
  String get general;

  /// No description provided for @notificationSettings.
  ///
  /// In en, this message translates to:
  /// **'Notification Settings'**
  String get notificationSettings;

  /// No description provided for @languageSettings.
  ///
  /// In en, this message translates to:
  /// **'Language Settings'**
  String get languageSettings;

  /// No description provided for @aboutSection.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get aboutSection;

  /// No description provided for @versionInfo.
  ///
  /// In en, this message translates to:
  /// **'Version Info'**
  String get versionInfo;

  /// No description provided for @helpCenter.
  ///
  /// In en, this message translates to:
  /// **'Help Center'**
  String get helpCenter;

  /// No description provided for @focusModeTitle.
  ///
  /// In en, this message translates to:
  /// **'Focus Mode'**
  String get focusModeTitle;

  /// No description provided for @pause.
  ///
  /// In en, this message translates to:
  /// **'Pause'**
  String get pause;

  /// No description provided for @start.
  ///
  /// In en, this message translates to:
  /// **'Start'**
  String get start;

  /// No description provided for @reset.
  ///
  /// In en, this message translates to:
  /// **'Reset'**
  String get reset;

  /// No description provided for @selectFileButton.
  ///
  /// In en, this message translates to:
  /// **'Select File'**
  String get selectFileButton;

  /// No description provided for @ocrRecognition.
  ///
  /// In en, this message translates to:
  /// **'OCR Recognition'**
  String get ocrRecognition;

  /// No description provided for @chooseImageOrText.
  ///
  /// In en, this message translates to:
  /// **'Choose image or enter text'**
  String get chooseImageOrText;

  /// No description provided for @takePhoto.
  ///
  /// In en, this message translates to:
  /// **'Take Photo'**
  String get takePhoto;

  /// No description provided for @chooseImage.
  ///
  /// In en, this message translates to:
  /// **'Choose Image'**
  String get chooseImage;

  /// No description provided for @paste.
  ///
  /// In en, this message translates to:
  /// **'Paste'**
  String get paste;

  /// No description provided for @pdfImportDisabled.
  ///
  /// In en, this message translates to:
  /// **'PDF Import (Temporarily Disabled)'**
  String get pdfImportDisabled;

  /// No description provided for @pdfImportDisabledMessage.
  ///
  /// In en, this message translates to:
  /// **'PDF import is temporarily disabled'**
  String get pdfImportDisabledMessage;

  /// No description provided for @waitingForSDKUpgrade.
  ///
  /// In en, this message translates to:
  /// **'Waiting for Flutter SDK 3.7.2+'**
  String get waitingForSDKUpgrade;

  /// No description provided for @back.
  ///
  /// In en, this message translates to:
  /// **'Back'**
  String get back;

  /// No description provided for @taskDetails.
  ///
  /// In en, this message translates to:
  /// **'Task Details'**
  String get taskDetails;

  /// No description provided for @dueTimeLabel.
  ///
  /// In en, this message translates to:
  /// **'Due Time:'**
  String get dueTimeLabel;

  /// No description provided for @priorityLabel.
  ///
  /// In en, this message translates to:
  /// **'Priority:'**
  String get priorityLabel;

  /// No description provided for @startFocusButton.
  ///
  /// In en, this message translates to:
  /// **'Start Focus'**
  String get startFocusButton;

  /// No description provided for @backButton.
  ///
  /// In en, this message translates to:
  /// **'Back'**
  String get backButton;

  /// No description provided for @continuesLearning.
  ///
  /// In en, this message translates to:
  /// **'Streak'**
  String get continuesLearning;

  /// No description provided for @total.
  ///
  /// In en, this message translates to:
  /// **'Total'**
  String get total;

  /// No description provided for @highPriority.
  ///
  /// In en, this message translates to:
  /// **'High Priority'**
  String get highPriority;

  /// No description provided for @completeAll.
  ///
  /// In en, this message translates to:
  /// **'Complete All'**
  String get completeAll;

  /// No description provided for @goAddTask.
  ///
  /// In en, this message translates to:
  /// **'Add Tasks'**
  String get goAddTask;

  /// No description provided for @refresh.
  ///
  /// In en, this message translates to:
  /// **'Refresh'**
  String get refresh;

  /// No description provided for @restOrAddTask.
  ///
  /// In en, this message translates to:
  /// **'Take a rest or add new tasks'**
  String get restOrAddTask;

  /// No description provided for @addNewTask.
  ///
  /// In en, this message translates to:
  /// **'Add New Task'**
  String get addNewTask;

  /// No description provided for @enterTaskName.
  ///
  /// In en, this message translates to:
  /// **'Enter task name'**
  String get enterTaskName;

  /// No description provided for @enterTaskDescription.
  ///
  /// In en, this message translates to:
  /// **'Enter task description'**
  String get enterTaskDescription;

  /// No description provided for @high.
  ///
  /// In en, this message translates to:
  /// **'High'**
  String get high;

  /// No description provided for @medium.
  ///
  /// In en, this message translates to:
  /// **'Medium'**
  String get medium;

  /// No description provided for @low.
  ///
  /// In en, this message translates to:
  /// **'Low'**
  String get low;

  /// No description provided for @close.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get close;

  /// No description provided for @priorityText.
  ///
  /// In en, this message translates to:
  /// **'Priority'**
  String get priorityText;

  /// No description provided for @status.
  ///
  /// In en, this message translates to:
  /// **'Status'**
  String get status;

  /// No description provided for @notCompleted.
  ///
  /// In en, this message translates to:
  /// **'Not Completed'**
  String get notCompleted;

  /// No description provided for @completedTime.
  ///
  /// In en, this message translates to:
  /// **'Completed Time'**
  String get completedTime;

  /// No description provided for @reminderSettings.
  ///
  /// In en, this message translates to:
  /// **'Reminder Settings'**
  String get reminderSettings;

  /// No description provided for @wrongQuestionBook.
  ///
  /// In en, this message translates to:
  /// **'Wrong Questions'**
  String get wrongQuestionBook;

  /// No description provided for @viewResults.
  ///
  /// In en, this message translates to:
  /// **'View Results'**
  String get viewResults;

  /// No description provided for @goalSettings.
  ///
  /// In en, this message translates to:
  /// **'Goal Settings'**
  String get goalSettings;
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) => <String>['en', 'zh'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {


  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en': return AppLocalizationsEn();
    case 'zh': return AppLocalizationsZh();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.'
  );
}
