BASE_URL = "https://rb.ru"

SECTIONS = {
    'news': '/news/',
    'stories': '/stories/',
    'opinions': '/columns/',
    'neuroprofiles': '/neuro/',
    'reviews': '/reviews/',
    'checklists': '/checklists/'
}

DEFAULT_MAX_WORKERS = 20
DEFAULT_DELAY = 0.3
DEFAULT_TIMEOUT = 15
DEFAULT_RETRIES = 5

ARTICLE_URL_PATTERN = r'/(news|stories|columns|opinions|neuroprofiles|reviews|checklists)/[^/?]+/?$'
FULL_URL_PATTERN = r'https?://(?:www\.)?rb\.ru/(news|stories|columns|opinions|neuroprofiles|reviews|checklists)/[^/?]+/?$'
