import 'package:flutter/material.dart';

class FiltersPanel extends StatelessWidget {
  final String? selectedContentType;
  final String? selectedCompany;
  final String? selectedTag;
  final ValueChanged<String?> onContentTypeChanged;
  final ValueChanged<String?> onCompanyChanged;
  final ValueChanged<String?> onTagChanged;

  const FiltersPanel({
    super.key,
    required this.selectedContentType,
    required this.selectedCompany,
    required this.selectedTag,
    required this.onContentTypeChanged,
    required this.onCompanyChanged,
    required this.onTagChanged,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Stack(
      clipBehavior: Clip.none, // Позволяем изображению выходить за границы
      children: [
        // Контент фильтров
        Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
          Row(
            children: [
              Icon(
                Icons.tune,
                size: 20,
                color: Colors.grey[600],
              ),
              const SizedBox(width: 8),
              Text(
                'Фильтры',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Вертикальное расположение фильтров
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Тип контента:',
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 8),
              _buildFilterChip(
                context,
                label: 'Тип',
                value: selectedContentType,
                options: const [
                  'news',
                  'stories',
                  'opinions',
                  'neuroprofiles',
                  'reviews',
                  'checklists',
                ],
                labels: const {
                  'news': 'Новости',
                  'stories': 'Истории',
                  'opinions': 'Мнения',
                  'neuroprofiles': 'Нейропрофайлы',
                  'reviews': 'Обзоры',
                  'checklists': 'Чек-листы',
                },
                onChanged: onContentTypeChanged,
              ),
              const SizedBox(height: 16),
              Text(
                'Компания:',
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 8),
              _buildFilterChip(
                context,
                label: 'Компания',
                value: selectedCompany,
                options: const [],
                labels: const {},
                onChanged: onCompanyChanged,
                isEditable: true,
              ),
              const SizedBox(height: 16),
              Text(
                'Тег:',
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 8),
              _buildFilterChip(
                context,
                label: 'Тег',
                value: selectedTag,
                options: const [],
                labels: const {},
                onChanged: onTagChanged,
                isEditable: true,
              ),
              const SizedBox(height: 16),
              // Кнопка сброса фильтров
              if (selectedContentType != null ||
                  selectedCompany != null ||
                  selectedTag != null)
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () {
                      onContentTypeChanged(null);
                      onCompanyChanged(null);
                      onTagChanged(null);
                    },
                    icon: const Icon(Icons.clear, size: 16),
                    label: const Text('Сбросить фильтры'),
                  ),
                ),
            ],
          ),
        ],
        ),
        ),
        // jordan внизу панели фильтров
        Positioned(
          left: -130, // Сдвигаем влево (было -170, подвинули на 1 см вправо = -130)
          bottom: -20, // Сдвигаем вниз на ~0.5 см (20px)
          child: IgnorePointer(
            child: SizedBox(
              width: 450, // Увеличиваем ширину, чтобы изображение не обрезалось при сдвиге влево
              height: 300,
              child: Container(
                decoration: BoxDecoration(
                  image: DecorationImage(
                    image: const AssetImage('assets/jordan.png'),
                    fit: BoxFit.cover,
                    alignment: Alignment.bottomLeft,
                    opacity: 0.7, // Затемнение изображения на 30%
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildFilterChip(
    BuildContext context, {
    required String label,
    required String? value,
    required List<String> options,
    required Map<String, String> labels,
    required ValueChanged<String?> onChanged,
    bool isEditable = false,
  }) {
    final theme = Theme.of(context);
    final hasValue = value != null;

    if (isEditable) {
      // Редактируемое поле (для компаний и тегов)
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: hasValue
              ? theme.colorScheme.primary.withOpacity(0.1)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: hasValue
                ? theme.colorScheme.primary
                : Colors.grey.withOpacity(0.3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 200,
              child: TextField(
                controller: TextEditingController(text: value ?? ''),
                onChanged: (text) {
                  onChanged(text.isEmpty ? null : text);
                },
                decoration: const InputDecoration(
                  hintText: 'введите...',
                  border: InputBorder.none,
                  isDense: true,
                  contentPadding: EdgeInsets.symmetric(horizontal: 4),
                ),
                style: theme.textTheme.bodySmall,
              ),
            ),
            if (hasValue)
              GestureDetector(
                onTap: () => onChanged(null),
                child: Icon(
                  Icons.close,
                  size: 16,
                  color: theme.colorScheme.primary,
                ),
              ),
          ],
        ),
      );
    }

    // Выпадающий список
    return PopupMenuButton<String?>(
      initialValue: value,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: hasValue
              ? theme.colorScheme.primary.withOpacity(0.1)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: hasValue
                ? theme.colorScheme.primary
                : Colors.grey.withOpacity(0.3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              hasValue ? (labels[value] ?? value) : 'Все',
              style: theme.textTheme.bodySmall?.copyWith(
                color: hasValue ? theme.colorScheme.primary : null,
                fontWeight: hasValue ? FontWeight.w500 : null,
              ),
            ),
            const SizedBox(width: 4),
            Icon(
              Icons.arrow_drop_down,
              size: 16,
              color: hasValue ? theme.colorScheme.primary : Colors.grey[600],
            ),
          ],
        ),
      ),
      onSelected: onChanged,
      itemBuilder: (context) => [
        const PopupMenuItem<String?>(
          value: null,
          child: Text('Все'),
        ),
        ...options.map(
          (option) => PopupMenuItem<String?>(
            value: option,
            child: Text(labels[option] ?? option),
          ),
        ),
      ],
    );
  }
}

