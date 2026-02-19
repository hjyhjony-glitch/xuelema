/// 导入结果模型
class ImportResult {
  final bool success;
  final int totalCount;
  final int successCount;
  final int errorCount;
  final List<String> errors;
  final List<QuestionImportModel> questions;

  ImportResult({
    required this.success,
    required this.totalCount,
    required this.successCount,
    required this.errorCount,
    required this.errors,
    required this.questions,
  });

  factory ImportResult.success(List<QuestionImportModel> questions) {
    return ImportResult(
      success: true,
      totalCount: questions.length,
      successCount: questions.length,
      errorCount: 0,
      errors: [],
      questions: questions,
    );
  }

  factory ImportResult.partial(
    List<QuestionImportModel> questions, 
    List<String> errors
  ) {
    return ImportResult(
      success: questions.isNotEmpty,
      totalCount: questions.length + errors.length,
      successCount: questions.length,
      errorCount: errors.length,
      errors: errors,
      questions: questions,
    );
  }

  factory ImportResult.failed(String error) {
    return ImportResult(
      success: false,
      totalCount: 0,
      successCount: 0,
      errorCount: 1,
      errors: [error],
      questions: [],
    );
  }
}

/// 导入题目模型
class QuestionImportModel {
  final String title;
  final String? options;
  final String answer;
  final String? explanation;
  final String subject;
  final String? difficulty;
  final int? questionType; // 1: 单选, 2: 多选, 3: 填空, 4: 判断

  QuestionImportModel({
    required this.title,
    this.options,
    required this.answer,
    this.explanation,
    required this.subject,
    this.difficulty,
    this.questionType,
  });

  factory QuestionImportModel.fromCsv(List<dynamic> row, List<String> headers) {
    final Map<String, dynamic> map = {};
    for (int i = 0; i < headers.length && i < row.length; i++) {
      map[headers[i]] = row[i].toString();
    }

    return QuestionImportModel(
      title: map['title'] ?? map['题目'] ?? '',
      options: map['options'] ?? map['选项'] ?? '',
      answer: map['answer'] ?? map['答案'] ?? '',
      explanation: map['explanation'] ?? map['解析'] ?? '',
      subject: map['subject'] ?? map['科目'] ?? '默认',
      difficulty: map['difficulty'] ?? map['难度'] ?? '中等',
      questionType: int.tryParse((map['questionType'] ?? map['题型'] ?? '1').toString()),
    );
  }

  bool isValid() {
    return title.isNotEmpty && answer.isNotEmpty;
  }
}
