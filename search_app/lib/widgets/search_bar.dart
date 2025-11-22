import 'package:flutter/material.dart';

class SearchBarWidget extends StatefulWidget {
  final TextEditingController controller;
  final VoidCallback onSearch;
  final bool isLoading;

  const SearchBarWidget({
    super.key,
    required this.controller,
    required this.onSearch,
    this.isLoading = false,
  });

  @override
  State<SearchBarWidget> createState() => _SearchBarWidgetState();
}

class _SearchBarWidgetState extends State<SearchBarWidget> {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: theme.colorScheme.outline.withOpacity(0.2),
        ),
        boxShadow: [
          BoxShadow(
            color: theme.colorScheme.primary.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: TextField(
        controller: widget.controller,
        onSubmitted: (_) => widget.onSearch(),
        decoration: InputDecoration(
          hintText: 'Поиск статей...',
          prefixIcon: Icon(
            Icons.search,
            color: theme.colorScheme.primary,
          ),
          suffixIcon: widget.isLoading
              ? const Padding(
                  padding: EdgeInsets.all(12),
                  child: SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                )
              : IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () {
                    widget.controller.clear();
                    widget.onSearch();
                  },
                ),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 20,
            vertical: 16,
          ),
        ),
        style: theme.textTheme.bodyLarge,
      ),
    );
  }
}

