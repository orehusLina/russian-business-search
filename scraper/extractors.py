"""
Модуль для извлечения уникальных полей из текста
(деньги, компании, люди)
"""

import re
from typing import List, Dict


class DataExtractor:
    """Класс для извлечения специфичных данных из текста"""
    
    # Словарь известных компаний для улучшения извлечения
    KNOWN_COMPANIES = {
        # Российские компании
        'Яндекс', 'Тинькофф', 'Сбер', 'ВТБ', 'Альфа-Банк', 'МТС', 'Мегафон',
        'Tele2', 'T2', 'Ozon', 'Wildberries', 'Авито', 'Юла', 'Деливери', 'Яндекс.Еда',
        'Сбербанк', 'Райффайзен', 'Газпром', 'Лукойл', 'Роснефть', 'T2 AdTech',
        'Яндекс.Музыка', 'Яндекс.Такси', 'Яндекс.Маркет', 'Яндекс.Директ',
        # Международные IT и технологические компании
        'Apple', 'Tesla', 'Google', 'Microsoft', 'Amazon', 'Meta', 'Facebook',
        'Netflix', 'Uber', 'Airbnb', 'Twitter', 'X', 'LinkedIn', 'Instagram',
        'WhatsApp', 'Telegram', 'Spotify', 'Adobe', 'Oracle', 'IBM', 'Intel',
        'Nvidia', 'Samsung', 'Sony', 'LG', 'Huawei', 'Xiaomi', 'Alibaba',
        'Tencent', 'Baidu', 'PayPal', 'Visa', 'Mastercard', 'Stripe',
        # Финансовые компании
        'Goldman Sachs', 'JPMorgan', 'Morgan Stanley', 'Citigroup', 'Bank of America',
        'Wells Fargo', 'Deutsche Bank', 'HSBC', 'Barclays', 'Credit Suisse',
        # Автомобильные компании
        'BMW', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Toyota', 'Honda', 'Nissan',
        'Ford', 'General Motors', 'Volvo', 'Porsche', 'Ferrari', 'Lamborghini',
        # Розничная торговля и маркетплейсы
        'eBay', 'Shopify', 'Walmart', 'Target', 'Costco', 'IKEA', 'Zara',
        'H&M', 'Nike', 'Adidas', 'Puma', 'Uniqlo',
        # Медиа и развлечения
        'Disney', 'Warner Bros', 'Universal', 'Paramount', 'HBO', 'Hulu',
        'YouTube', 'TikTok', 'Snapchat', 'Pinterest', 'Reddit',
        # Другие известные бренды
        'Coca-Cola', 'Pepsi', 'McDonald\'s', 'Starbucks', 'KFC', 'Subway',
        'Nestle', 'Unilever', 'Procter & Gamble', 'Johnson & Johnson',
    }
    
    # Минимальный набор стоп-слов только для критичных случаев
    # Основная фильтрация через улучшенные паттерны
    
    @staticmethod
    def extract_money(text: str) -> List[Dict]:
        """
        Извлечение упоминаний денежных сумм из текста
        Примеры: "220 млн ₽", "$15 млн", "1,5 млн рублей"
        
        Args:
            text: Текст для анализа
            
        Returns:
            Список словарей с информацией о деньгах:
            [{'amount': '220', 'multiplier': 'млн', 'currency': '₽', 'original': '220 млн ₽'}, ...]
        """
        money_list = []
        
        # Паттерны для извлечения денежных сумм с полной информацией
        patterns = [
            # "220 млн ₽" или "220 млн рублей"
            r'(\d+(?:[.,]\d+)?)\s*(млн|млрд|тыс\.?)\s*([₽$€]|рублей?|долларов?|евро)',
            # "$15 млн" или "₽15 млн"
            r'([₽$€])\s*(\d+(?:[.,]\d+)?)\s*(млн|млрд|тыс\.?)',
            # "15 млн долларов" или "15 млн рублей"
            r'(\d+(?:[.,]\d+)?)\s*(млн|млрд|тыс\.?)\s*(рублей?|долларов?|евро)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                original = match.group(0)
                
                money_info = {
                    'amount': '',
                    'multiplier': '',
                    'currency': '',
                    'original': original
                }
                
                # Обрабатываем разные форматы паттернов
                if len(groups) == 3:
                    if groups[0].isdigit() or '.' in groups[0] or ',' in groups[0]:
                        # Формат: "220 млн ₽"
                        money_info['amount'] = groups[0].replace(',', '.')
                        money_info['multiplier'] = groups[1].lower().rstrip('.')
                        currency = groups[2].lower()
                        if currency in ['₽', 'рублей', 'рубля', 'рубль']:
                            money_info['currency'] = '₽'
                        elif currency in ['$', 'долларов', 'доллара', 'доллар']:
                            money_info['currency'] = '$'
                        elif currency in ['€', 'евро']:
                            money_info['currency'] = '€'
                        else:
                            money_info['currency'] = currency
                    else:
                        # Формат: "$15 млн"
                        money_info['currency'] = groups[0]
                        money_info['amount'] = groups[1].replace(',', '.')
                        money_info['multiplier'] = groups[2].lower().rstrip('.')
                
                # Нормализуем multiplier
                if money_info['multiplier']:
                    if 'тыс' in money_info['multiplier']:
                        money_info['multiplier'] = 'тыс'
                    elif 'млн' in money_info['multiplier']:
                        money_info['multiplier'] = 'млн'
                    elif 'млрд' in money_info['multiplier']:
                        money_info['multiplier'] = 'млрд'
                
                # Добавляем только если есть все необходимые поля
                if money_info['amount'] and money_info['multiplier']:
                    money_list.append(money_info)
        
        # Убираем дубликаты по оригинальной строке
        seen = set()
        unique_money = []
        for money in money_list:
            key = money['original'].lower()
            if key not in seen:
                seen.add(key)
                unique_money.append(money)
        
        return unique_money
    
    @classmethod
    def extract_companies(cls, text: str) -> List[str]:
        """
        Извлечение упоминаний компаний через улучшенные паттерны
        
        Args:
            text: Текст для анализа
            
        Returns:
            Список найденных компаний
        """
        companies = set()
        
        # 1. Известные компании из словаря (точное совпадение слова)
        text_lower = text.lower()
        for company in cls.KNOWN_COMPANIES:
            pattern = r'\b' + re.escape(company.lower()) + r'\b'
            if re.search(pattern, text_lower):
                companies.add(company)
        
        # 2. Компании в кавычках «...» или "..."
        # Ищем паттерн: «Название» или "Название" где название начинается с заглавной
        quoted_patterns = [
            r'«([А-ЯЁA-Z][А-Яа-яёA-Za-z0-9\.\s]{2,40}?)»',  # Русские кавычки
            r'"([А-ЯЁA-Z][А-Яа-яёA-Za-z0-9\.\s]{2,40}?)"',   # Английские кавычки
        ]
        for pattern in quoted_patterns:
            quoted = re.findall(pattern, text)
            for q in quoted:
                q_clean = q.strip()
                # Проверяем что это не прилагательное и не общее слово
                if (len(q_clean) >= 2 and 
                    q_clean[0].isupper() and
                    not re.match(r'^[А-ЯЁа-яё]+(?:ых|их|ому|ему|ой|ей|ая|ое|ую)$', q_clean.lower()) and
                    # Исключаем общие слова
                    not re.match(r'^(?:серых|черных|белых|новых|старых)', q_clean.lower())):
                    companies.add(q_clean)
        
        # 3. Паттерн: "компания/стартап/оператор/бренд + Название" (со склонениями)
        # Склонения слова "компания": компания, компании, компаний, компанию, компанией, компаниям
        # Склонения слова "оператор": оператор, оператора, оператору, оператором, операторы, операторов
        company_context_pattern = r'(?:компани(?:я|и|ей|ю|ей|ям|ями)|стартап(?:а|у|ом|ы|ов|ам|ами)?|проект(?:а|у|ом|ы|ов|ам|ами)?|сервис(?:а|у|ом|ы|ов|ам|ами)?|банк(?:а|у|ом|и|ов|ам|ами)?|оператор(?:а|у|ом|ы|ов|ам|ами)?|бренд(?:а|у|ом|ы|ов|ам|ами)?|платформ(?:а|ы|е|у|ой|ам|ами)?|экосистем(?:а|ы|е|у|ой|ам|ами)?)\s+([А-ЯЁA-Z][А-Яа-яёA-Za-z0-9\.\s]{2,35}?)(?:\s|,|\.|$|—|–|:|;|\(|\))'
        matches = re.findall(company_context_pattern, text, re.IGNORECASE)
        for match in matches:
            match_clean = match.strip()
            # Убираем лишние пробелы и проверяем формат
            match_clean = ' '.join(match_clean.split())
            # Исключаем если заканчивается на прилагательное или предлог
            if (2 <= len(match_clean) <= 40 and
                match_clean[0].isupper() and
                not re.search(r'(?:ых|их|ому|ему|ой|ей|ая|ое|ую|ем|им|ую)$', match_clean.lower()) and
                not re.match(r'^(?:при|про|для|над|под|без|от|до|из|к|с|о|об|на|по|за)\s', match_clean.lower())):
                companies.add(match_clean)
        
        # 4. Названия в формате "Буква+Цифра" или "Буква+Цифра + Слова" (T2, T2 AdTech)
        tech_company_pattern = r'\b([A-Z]\d+(?:\s+[A-Z][a-z]+)*)\b'
        tech_matches = re.findall(tech_company_pattern, text)
        for match in tech_matches:
            if len(match) >= 2:
                companies.add(match)
        
        # 5. Аббревиатуры из словаря известных компаний (МТС, ВТБ, Сбер)
        # Только если это точное совпадение из словаря
        for company in cls.KNOWN_COMPANIES:
            if len(company) <= 5 and company.isupper():  # Только короткие аббревиатуры
                pattern = r'\b' + re.escape(company) + r'\b'
                if re.search(pattern, text):
                    companies.add(company)
        
        # 6. Названия с точками (Яндекс.Еда, Яндекс.Музыка) - только если есть точка
        dotted_pattern = r'\b([А-ЯЁA-Z][А-Яа-яёA-Za-z]+\.(?:[А-ЯЁA-Z][а-яёa-z]+)+)\b'
        dotted_matches = re.findall(dotted_pattern, text)
        for match in dotted_matches:
            if len(match) >= 5:  # Минимум 5 символов для названий с точками
                companies.add(match)
        
        # Финальная фильтрация через паттерны (без стоп-слов)
        filtered = []
        for c in companies:
            c_clean = c.strip()
            
            # Проверяем через паттерны, а не через стоп-слова
            if (3 <= len(c_clean) <= 50 and
                c_clean[0].isupper() and
                # Исключаем прилагательные через паттерн
                not re.search(r'(?:ых|их|ому|ему|ой|ей|ая|ое|ую|ем|им)$', c_clean.lower()) and
                # Исключаем предлоги в начале через паттерн
                not re.match(r'^(?:при|про|для|над|под|без|от|до|из|к|с|о|об|на|по|за)\s', c_clean.lower()) and
                # Исключаем географические названия через паттерн (названия городов/стран обычно в определенных контекстах)
                not re.match(r'^(?:росси|москв|петербург|санкт)', c_clean.lower()) and
                # Исключаем общие слова через паттерн (существительные в определенных формах)
                not re.match(r'^(?:рынок|решение|требование|выбор|при)', c_clean.lower())):
                filtered.append(c_clean)
        
        return list(set(filtered))
    
    @staticmethod
    def extract_people(text: str) -> List[str]:
        """
        Извлечение имен людей (паттерн: Имя Фамилия с заглавных букв)
        
        Args:
            text: Текст для анализа
            
        Returns:
            Список найденных имен (максимум 10)
        """
        # Слова, которые не являются именами людей
        not_people = {
            'республика', 'корея', 'яблоко', 'яндекс', 'россия', 'москва',
            'российский', 'московский', 'российская', 'московская',
            'северная', 'южная', 'восточная', 'западная',
            'компания', 'компании', 'компаний', 'компанию',
            'оператор', 'операторы', 'операторов',
            'банк', 'банка', 'банку', 'банки', 'банков',
            'рынок', 'рынка', 'рынке', 'рынком',
            'решение', 'решения', 'решений',
            'требование', 'требования', 'требований',
            'выбор', 'выбора', 'выбору',
            'при', 'про', 'для', 'над', 'под', 'без',
            'новый', 'новая', 'новое', 'новые',
            'старый', 'старая', 'старое', 'старые',
        }
        
        # Паттерн для русских имен: Имя Фамилия
        pattern = r'\b([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)\b'
        matches = re.findall(pattern, text)
        people = [f"{first} {last}" for first, last in matches]
        
        # Фильтруем слишком короткие, общие слова и не-имена
        filtered = []
        for p in people:
            first, last = p.split()
            first_lower = first.lower()
            last_lower = last.lower()
            
            # Проверяем что это не стоп-слова
            if (len(first) > 2 and len(last) > 2 and
                first_lower not in not_people and
                last_lower not in not_people and
                # Исключаем прилагательные
                not first_lower.endswith(('ый', 'ая', 'ое', 'ие', 'ой', 'ей')) and
                not last_lower.endswith(('ый', 'ая', 'ое', 'ие', 'ой', 'ей')) and
                # Исключаем географические названия
                not re.match(r'^(северн|южн|восточн|западн|российск|московск)', first_lower) and
                not re.match(r'^(северн|южн|восточн|западн|российск|московск)', last_lower)):
                filtered.append(p)
        
        return list(set(filtered))[:10]  # Ограничиваем количество

