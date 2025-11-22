import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/article.dart';

class SearchService {
  final String baseUrl;

  SearchService({this.baseUrl = 'http://localhost:8000'});

  /// Поиск статей
  Future<SearchResponse> search({
    required String query,
    int size = 20,
    int from = 0,
    String? contentType,
    String? company,
    String? tag,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/search').replace(queryParameters: {
        'q': query,
        'size': size.toString(),
        'from': from.toString(),
        if (contentType != null) 'content_type': contentType,
        if (company != null) 'company': company,
        if (tag != null) 'tag': tag,
      });

      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return SearchResponse.fromJson(json.decode(response.body));
      } else {
        throw Exception('Ошибка поиска: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Ошибка подключения: $e');
    }
  }

  /// Получить статистику
  Future<Stats> getStats() async {
    try {
      final uri = Uri.parse('$baseUrl/stats');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return Stats.fromJson(json.decode(response.body));
      } else {
        throw Exception('Ошибка получения статистики: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Ошибка подключения: $e');
    }
  }

  /// Проверка здоровья API
  Future<bool> checkHealth() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['status'] == 'ok';
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}

