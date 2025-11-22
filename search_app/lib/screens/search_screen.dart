import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/article.dart';
import '../services/search_service.dart';
import '../widgets/article_card.dart';
import '../widgets/search_bar.dart';
import '../widgets/filters_panel.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final SearchService _searchService = SearchService();
  final TextEditingController _searchController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  SearchResponse? _searchResponse;
  bool _isLoading = false;
  String _errorMessage = '';
  bool _isHealthOk = false;

  // Фильтры
  String? _selectedContentType;
  String? _selectedCompany;
  String? _selectedTag;
  int _currentPage = 0;
  final int _pageSize = 20;

  @override
  void initState() {
    super.initState();
    _checkHealth();
    _loadStats();
    // Загружаем тестовые данные для демонстрации
    _loadTestData();
  }

  void _loadTestData() {
    // Тестовые данные для предпросмотра
    final testArticles = [
      Article(
        id: '1',
        url: 'https://rb.ru/news/tilteh-noun/',
        title: 'Фонд «ТилТех Капитал» консолидировал ритейлера Noun',
        contentType: 'news',
        author: 'Наталья Гормалева',
        date: '14 апреля 2025, 17:16',
        description: 'Венчурный фонд Андрея Кривенко «ТилТех Капитал» приобрел 100% сети магазинов женской одежды Noun у основателя Семена Пименова.',
        tags: ['Бизнес'],
        companies: ['ТилТех Капитал'],
        people: ['Семена Пименова', 'Андрея Кривенко'],
        money: [],
        score: 8.5,
      ),
      Article(
        id: '2',
        url: 'https://rb.ru/news/posle-novosti-o-vozmozhnom-poluchenii-1-trln-ilon-mask-poteryal-10-mlrd-na-akciyah-tesla-kotorye-rezko-proseli/',
        title: 'После новости о возможном получении 1 трлн Илон Маск потерял 10 млрд на акциях Tesla, которые резко просели',
        contentType: 'news',
        author: 'Данила Куликовский',
        date: '14 ноября 2025, 17:07',
        description: 'Акции Tesla упали после новостей о возможном получении компанией 1 трлн долларов.',
        tags: ['Личное', 'Бизнес', 'Деньги'],
        companies: ['Tesla'],
        people: ['Илона Маска'],
        money: [
          Money(amount: '10', multiplier: 'млрд', currency: '\$', original: '\$10 млрд'),
          Money(amount: '1', multiplier: 'трлн', currency: '\$', original: '1 трлн \$'),
        ],
        score: 9.2,
      ),
      Article(
        id: '3',
        url: 'https://rb.ru/news/top-sales-markeplaces/',
        title: 'Что россияне чаще всего покупали в 2023 году: аналитика по продажам на маркетплейсах',
        contentType: 'news',
        author: 'Кирилл Билык',
        date: '15 июля 2025, 16:56',
        description: 'Аналитики составили топ самых продаваемых товаров на популярных российских маркетплейсах. По итогам 2023 года лидером по выручке на Wildberries стали товары для женщин, на Ozon – товары для дома, на «Яндекс.Маркете» – товары из категории «Здоровье».',
        tags: ['Маркетплейсы', 'Россия'],
        companies: ['Wildberries', 'Ozon', 'Яндекс.Маркете'],
        people: [],
        money: [],
        score: 7.8,
      ),
      Article(
        id: '4',
        url: 'https://rb.ru/news/ne-proshyol-test-na-empatiyu-grok-priznan-naibolee-opasnym-ii-dlya-lyudej-s-mentalnymi-problemami/',
        title: 'ИИ Маска «наиболее опасна» для людей с уязвимой психикой',
        contentType: 'news',
        author: 'Данила Куликовский',
        date: '14 ноября 2025, 13:16',
        description: 'ИИ-модель Grok, созданная под руководством Илона Маска, признана наименее безопасной для людей, переживающих эмоциональный кризис. По данным исследования Rosebud, на которое ссылается Forbes, Grok ошибался в 60% запросов о ментальном здоровье.',
        tags: ['Искусственный интеллект', 'Технологии'],
        companies: [],
        people: ['Илона Маска'],
        money: [],
        score: 8.1,
      ),
      Article(
        id: '5',
        url: 'https://rb.ru/news/avito-vernulsya-app-store/',
        title: 'Приложение «Авито» вернулось в App Store, в РФ ввезут просекко из Бразилии: главное 24 июля',
        contentType: 'news',
        author: 'Команда Русбейс',
        date: '04 июля 2025, 18:46',
        description: 'Мобильное приложение российского классифайда «Авито» вернулось в App Store, работодатели не готовы отказываться от перспективных соискателей, несмотря на нехватку нужных для вакансии навыков и компетенций и другие события 24 июля.',
        tags: [],
        companies: ['Авито'],
        people: [],
        money: [],
        score: 6.5,
      ),
    ];

    setState(() {
      _searchResponse = SearchResponse(
        total: 5,
        results: testArticles,
        took: 15,
      );
    });
  }

  Future<void> _checkHealth() async {
    final isOk = await _searchService.checkHealth();
    setState(() {
      _isHealthOk = isOk;
    });
  }

  Future<void> _loadStats() async {
    try {
      await _searchService.getStats();
    } catch (e) {
      // Игнорируем ошибки при загрузке статистики
    }
  }

  Future<void> _performSearch({bool resetPage = true}) async {
    if (_searchController.text.trim().isEmpty) {
      setState(() {
        _searchResponse = null;
        _errorMessage = '';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = '';
      if (resetPage) {
        _currentPage = 0;
      }
    });

    try {
      final response = await _searchService.search(
        query: _searchController.text.trim(),
        size: _pageSize,
        from: _currentPage * _pageSize,
        contentType: _selectedContentType,
        company: _selectedCompany,
        tag: _selectedTag,
      );

      setState(() {
        if (resetPage) {
          _searchResponse = response;
        } else {
          // Добавляем результаты к существующим
          final existingResults = _searchResponse?.results ?? [];
          _searchResponse = SearchResponse(
            total: response.total,
            results: [...existingResults, ...response.results],
            took: response.took,
          );
        }
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  void _loadMore() {
    if (!_isLoading &&
        _searchResponse != null &&
        _searchResponse!.results.length < _searchResponse!.total) {
      setState(() {
        _currentPage++;
      });
      _performSearch(resetPage: false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      body: Stack(
        children: [
          // Основной фон с money.png (без затемнения)
          Container(
            decoration: BoxDecoration(
              image: DecorationImage(
                image: const AssetImage('assets/money.png'),
                fit: BoxFit.cover,
              ),
            ),
          ),
          // matthew в правом верхнем углу (сдвинут вниз и вправо)
          Positioned(
            right: -60, // Сдвигаем вправо на 60px (еще больше)
            top: 200, // Сдвигаем вниз на ~200px
            child: IgnorePointer(
              child: Container(
                width: 200,
                height: 200,
                decoration: BoxDecoration(
                  image: DecorationImage(
                    image: const AssetImage('assets/matthew.png'),
                    fit: BoxFit.cover,
                    alignment: Alignment.topRight,
                  ),
                ),
              ),
            ),
          ),
          // Затемнение поверх всех изображений (но под контентом)
          IgnorePointer(
            child: Container(
              decoration: BoxDecoration(
                color: isDark ? Colors.grey[900]?.withOpacity(0.7) : Colors.grey[50]?.withOpacity(0.8),
              ),
            ),
          ),
          // Контент поверх всего
          SafeArea(
            child: Column(
              children: [
                // Заголовок и поисковая строка сверху
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surface,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 10,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.search,
                            color: theme.colorScheme.primary,
                            size: 32,
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Russian Business Search',
                            style: theme.textTheme.headlineMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: theme.colorScheme.primary,
                            ),
                          ),
                          const Spacer(),
                          // Статус подключения
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: _isHealthOk
                                  ? Colors.green.withOpacity(0.1)
                                  : Colors.red.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Container(
                                  width: 8,
                                  height: 8,
                                  decoration: BoxDecoration(
                                    color: _isHealthOk ? Colors.green : Colors.red,
                                    shape: BoxShape.circle,
                                  ),
                                ),
                                const SizedBox(width: 6),
                                Text(
                                  _isHealthOk ? 'Подключено' : 'Не подключено',
                                  style: theme.textTheme.bodySmall,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      // Поисковая строка
                      SearchBarWidget(
                        controller: _searchController,
                        onSearch: () => _performSearch(),
                        isLoading: _isLoading,
                      ),
                    ],
                  ),
                ),

                // Основной контент: фильтры слева, результаты справа
                Expanded(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Фильтры слева
                      Container(
                        width: 280,
                        clipBehavior: Clip.none, // Позволяем содержимому выходить за границы
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surface,
                          border: Border(
                            right: BorderSide(
                              color: Colors.grey.withOpacity(0.2),
                            ),
                          ),
                        ),
                        child: FiltersPanel(
                          selectedContentType: _selectedContentType,
                          selectedCompany: _selectedCompany,
                          selectedTag: _selectedTag,
                          onContentTypeChanged: (value) {
                            setState(() {
                              _selectedContentType = value;
                            });
                            _performSearch();
                          },
                          onCompanyChanged: (value) {
                            setState(() {
                              _selectedCompany = value;
                            });
                            _performSearch();
                          },
                          onTagChanged: (value) {
                            setState(() {
                              _selectedTag = value;
                            });
                            _performSearch();
                          },
                        ),
                      ),

                      // Результаты справа
                      Expanded(
                        child: _buildResults(theme),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResults(ThemeData theme) {
    if (_isLoading && _searchResponse == null) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_errorMessage.isNotEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red[300],
            ),
            const SizedBox(height: 16),
            Text(
              'Ошибка',
              style: theme.textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Text(
                _errorMessage,
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ),
          ],
        ),
      );
    }

    if (_searchResponse == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search,
              size: 80,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              'Введите запрос для поиска',
              style: theme.textTheme.headlineSmall?.copyWith(
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      );
    }

    if (_searchResponse!.results.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search_off,
              size: 80,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              'Ничего не найдено',
              style: theme.textTheme.headlineSmall?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Попробуйте изменить запрос или фильтры',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: Colors.grey[500],
              ),
            ),
          ],
        ),
      );
    }

    return NotificationListener<ScrollNotification>(
      onNotification: (notification) {
        if (notification is ScrollEndNotification) {
          final maxScroll = _scrollController.position.maxScrollExtent;
          final currentScroll = _scrollController.position.pixels;
          if (currentScroll >= maxScroll * 0.8) {
            _loadMore();
          }
        }
        return false;
      },
      child: ListView.builder(
        controller: _scrollController,
        padding: const EdgeInsets.all(16),
        itemCount: _searchResponse!.results.length + 1,
        itemBuilder: (context, index) {
          if (index == _searchResponse!.results.length) {
            // Индикатор загрузки в конце списка
            if (_isLoading) {
              return const Padding(
                padding: EdgeInsets.all(16),
                child: Center(child: CircularProgressIndicator()),
              );
            }
            if (_searchResponse!.results.length < _searchResponse!.total) {
              return Padding(
                padding: const EdgeInsets.all(16),
                child: Center(
                  child: Text(
                    'Показано ${_searchResponse!.results.length} из ${_searchResponse!.total}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ),
              );
            }
            return const SizedBox.shrink();
          }

          return ArticleCard(
            article: _searchResponse!.results[index],
            searchQuery: _searchController.text,
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }
}

