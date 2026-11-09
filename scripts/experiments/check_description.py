from scripts.load_data import load_recipes
import re

def check_time_and_kitchen(ds) -> tuple[int, int, list[str], list[str]]:
    """Проверка описания рецептов на содержание времени приготовления и наименования кухни"""

    count_minute = 0        # Количество рецептов с временем приготовления в описании
    count_kitchen = 0       # Количество рецептов с названием кухни в описании
    examples_kitchen = []   # Образцы названий кухонь
    examples_minute = []    # Образцы времени приготовления

    for recipe in ds:
        if not recipe['description']:
            continue
        desc = recipe['description'].lower()
        match_minute = re.search(r"(\d+)\s+мин", desc, re.IGNORECASE)
        match_kitchen = re.search(r"(\w+)\s+кухн", desc, re.IGNORECASE)
        if match_minute:
            count_minute += 1
            if len(examples_minute) < 5:
                examples_minute.append(match_minute.group(1))
        if match_kitchen:
            count_kitchen += 1
            if len(examples_kitchen) < 5:
                examples_kitchen.append(match_kitchen.group(1))

    return (count_minute, count_kitchen, examples_minute, examples_kitchen)

def print_checked_time_and_kitchen(ds, check_list:tuple[int, int, list[str], list[str]]):
    """Вывод в консоль результатов проверки времени приготовления и наименования кухни"""

    print(f"Всего рецептов: {len(ds)}")
    print(f"Количество рецептов с временем приготовления в описании: {check_list[0]}")
    print(f"Извлеченные примеры: ")
    print(*check_list[2], sep=',')
    print(f"Количество рецептов с названием кухни в описании: {check_list[1]}")
    print(f"Извлеченные примеры: ")
    print(*check_list[3], sep=',')

def check_description_prefix(ds, count_char=150) -> None:
    """Проверка префикса описаний"""

    for recipe in ds:
        if not recipe['description']:
            continue
        print(recipe['description'][:count_char] + "\n")

def check_keywords_in_description(ds, keywords: list[str]) -> int:
    """Проверка описания на содержание ключевых слов"""

    count_containing = 0
    for recipe in ds:
        if not recipe['description']:
            continue
        result = any(word in recipe['description'] for word in keywords)
        if result: count_containing += 1
    return count_containing

def print_checked_keywords_in_description(ds, count_containing: int) -> None:
    """Вывод в консоль результатов проверки описания на содержание ключевых слов"""

    print(f"Всего рецептов: {len(ds)}")
    print(f"Количество описаний с ключевыми словами: {count_containing}")
    print(f"Процент описаний с ключевыми словами: {(count_containing / len(ds) * 100):.2f}%")

def main():
    ds = load_recipes(limit=20)
    # print_checked_time_and_kitchen(ds, check_time_and_kitchen(ds))
    check_description_prefix(ds)
    keywords = ['быстр', 'прост', 'легк', 'диет', 'праздничн', 'детск', 'вегетарианск', 'летн', 'зимн']
    print_checked_keywords_in_description(ds, check_keywords_in_description(ds, keywords))

if __name__ == "__main__":
    main()