def extract_nickname(full_string):
    """Извлекает чистый никнейм из строки формата 'ip@nickname' или возвращает исходную строку"""
    if not full_string:
        return None
    if '@' in full_string:
        return full_string.split('@')[-1]
    return full_string