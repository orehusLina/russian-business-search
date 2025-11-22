import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/article.dart';

class ArticleCard extends StatelessWidget {
  final Article article;
  final String searchQuery;

  const ArticleCard({
    super.key,
    required this.article,
    required this.searchQuery,
  });

  String _getContentTypeLabel(String type) {
    const labels = {
      'news': 'Новость',
      'stories': 'История',
      'opinions': 'Мнение',
      'neuroprofiles': 'Нейропрофайл',
      'reviews': 'Обзор',
      'checklists': 'Чек-лист',
    };
    return labels[type] ?? type;
  }

  Color _getContentTypeColor(String type, BuildContext context) {
    final theme = Theme.of(context);
    final colors = {
      'news': Colors.blue,
      'stories': Colors.purple,
      'opinions': Colors.orange,
      'neuroprofiles': Colors.teal,
      'reviews': Colors.green,
      'checklists': Colors.amber,
    };
    return colors[type] ?? theme.colorScheme.primary;
  }

  String _highlightText(String text, String query) {
    if (query.isEmpty) return text;
    final lowerText = text.toLowerCase();
    final lowerQuery = query.toLowerCase();
    if (!lowerText.contains(lowerQuery)) return text;

    final regex = RegExp(query, caseSensitive: false);
    return text.replaceAllMapped(
      regex,
      (match) => '**${match.group(0)}**',
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: () {
          // Открыть статью в новой вкладке
          // В веб-приложении можно использовать url_launcher
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Заголовок и тип контента
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: _getContentTypeColor(
                              article.contentType, context)
                          .withOpacity(0.1),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      _getContentTypeLabel(article.contentType),
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: _getContentTypeColor(
                            article.contentType, context),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const Spacer(),
                  if (article.score > 0)
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.star,
                          size: 14,
                          color: Colors.amber[700],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          article.score.toStringAsFixed(1),
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                ],
              ),
              const SizedBox(height: 12),

              // Заголовок статьи
              if (article.title.isNotEmpty)
                Text(
                  article.title,
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),

              const SizedBox(height: 8),

              // Описание
              if (article.description.isNotEmpty)
                Text(
                  article.description,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[700],
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),

              const SizedBox(height: 12),

              // Метаданные
              Wrap(
                spacing: 16,
                runSpacing: 8,
                children: [
                  if (article.author.isNotEmpty)
                    _buildMetaItem(
                      context,
                      Icons.person,
                      article.author,
                    ),
                  if (article.date.isNotEmpty)
                    _buildMetaItem(
                      context,
                      Icons.calendar_today,
                      article.date,
                    ),
                ],
              ),

              // Теги, компании, люди
              if (article.tags.isNotEmpty ||
                  article.companies.isNotEmpty ||
                  article.people.isNotEmpty) ...[
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    ...article.tags.take(3).map(
                          (tag) => _buildChip(
                            context,
                            tag,
                            Icons.label,
                            Colors.blue,
                          ),
                        ),
                    ...article.companies.take(2).map(
                          (company) => _buildChip(
                            context,
                            company,
                            Icons.business,
                            Colors.green,
                          ),
                        ),
                    ...article.people.take(2).map(
                          (person) => _buildChip(
                            context,
                            person,
                            Icons.person,
                            Colors.orange,
                          ),
                        ),
                  ],
                ),
              ],

              // Деньги
              if (article.money.isNotEmpty) ...[
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  children: article.money.take(3).map(
                    (money) => Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.green.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: Colors.green.withOpacity(0.3),
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.attach_money,
                            size: 16,
                            color: Colors.green[700],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            money.formatted,
                            style: theme.textTheme.labelMedium?.copyWith(
                              color: Colors.green[700],
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ).toList(),
                ),
              ],

              const SizedBox(height: 12),

              // Ссылка
              Row(
                children: [
                  Icon(
                    Icons.link,
                    size: 14,
                    color: theme.colorScheme.primary,
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      article.url,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.primary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMetaItem(BuildContext context, IconData icon, String text) {
    final theme = Theme.of(context);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: Colors.grey[600]),
        const SizedBox(width: 4),
        Text(
          text,
          style: theme.textTheme.bodySmall?.copyWith(
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildChip(
    BuildContext context,
    String label,
    IconData icon,
    Color color,
  ) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: color.withOpacity(0.3),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: theme.textTheme.labelSmall?.copyWith(
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

