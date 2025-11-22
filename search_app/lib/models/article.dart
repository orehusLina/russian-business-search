/// Модель статьи
class Article {
  final String id;
  final String url;
  final String title;
  final String contentType;
  final String author;
  final String date;
  final String description;
  final List<String> tags;
  final List<String> companies;
  final List<String> people;
  final List<Money> money;
  final double score;
  final Map<String, dynamic>? highlight;

  Article({
    required this.id,
    required this.url,
    required this.title,
    required this.contentType,
    required this.author,
    required this.date,
    required this.description,
    required this.tags,
    required this.companies,
    required this.people,
    required this.money,
    required this.score,
    this.highlight,
  });

  factory Article.fromJson(Map<String, dynamic> json) {
    return Article(
      id: json['id']?.toString() ?? '',
      url: json['url']?.toString() ?? '',
      title: json['title']?.toString() ?? '',
      contentType: json['content_type']?.toString() ?? '',
      author: json['author']?.toString() ?? '',
      date: json['date']?.toString() ?? '',
      description: json['description']?.toString() ?? '',
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      companies: (json['companies'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      people: (json['people'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      money: (json['money'] as List<dynamic>?)
              ?.map((m) => Money.fromJson(m))
              .toList() ??
          [],
      score: (json['score'] ?? 0.0).toDouble(),
      highlight: json['highlight'] as Map<String, dynamic>?,
    );
  }
}

/// Модель денежной суммы
class Money {
  final String amount;
  final String multiplier;
  final String currency;
  final String original;

  Money({
    required this.amount,
    required this.multiplier,
    required this.currency,
    required this.original,
  });

  factory Money.fromJson(Map<String, dynamic> json) {
    return Money(
      amount: json['amount']?.toString() ?? '',
      multiplier: json['multiplier']?.toString() ?? '',
      currency: json['currency']?.toString() ?? '',
      original: json['original']?.toString() ?? '',
    );
  }

  String get formatted => '$amount $multiplier $currency';
}

/// Модель ответа поиска
class SearchResponse {
  final int total;
  final List<Article> results;
  final int took;

  SearchResponse({
    required this.total,
    required this.results,
    required this.took,
  });

  factory SearchResponse.fromJson(Map<String, dynamic> json) {
    return SearchResponse(
      total: json['total'] ?? 0,
      results: (json['results'] as List<dynamic>?)
              ?.map((r) => Article.fromJson(r))
              .toList() ??
          [],
      took: json['took'] ?? 0,
    );
  }
}

/// Модель статистики
class Stats {
  final int totalArticles;
  final Map<String, int> contentTypes;
  final List<StatItem> topCompanies;
  final List<StatItem> topTags;

  Stats({
    required this.totalArticles,
    required this.contentTypes,
    required this.topCompanies,
    required this.topTags,
  });

  factory Stats.fromJson(Map<String, dynamic> json) {
    return Stats(
      totalArticles: json['total_articles'] ?? 0,
      contentTypes: Map<String, int>.from(json['content_types'] ?? {}),
      topCompanies: (json['top_companies'] as List<dynamic>?)
              ?.map((c) => StatItem.fromJson(c))
              .toList() ??
          [],
      topTags: (json['top_tags'] as List<dynamic>?)
              ?.map((t) => StatItem.fromJson(t))
              .toList() ??
          [],
    );
  }
}

class StatItem {
  final String name;
  final int count;

  StatItem({required this.name, required this.count});

  factory StatItem.fromJson(Map<String, dynamic> json) {
    return StatItem(
      name: json['name'] ?? '',
      count: json['count'] ?? 0,
    );
  }
}

