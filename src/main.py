import logging

from src.agent.graph import app

# Конфигурация для работы с потоками
THREAD_CONFIG = {"configurable": {"thread_id": "cli"}}


def main():
    logging.basicConfig(level=logging.INFO)
    print("Инициализация агента...")
    first_query = True
    # Бесконечный цикл для продолжения общения с агентом
    while True:

        if first_query:
            query = input("\nЧто вы желаете приготовить? (или 'выход' для завершения):\n")
            first_query = False
        else:
            query = input("\nЧто делаем дальше?\n")

        if query.lower() in ["выход", "exit", "quit"]:
            print("\nЗавершение работы агента.\n")
            break

        if not query.strip():
            print("Кажется, вы ничего не написали. Пожалуйста, введите запрос.")
            continue

        result = app.invoke(
            {
                "messages": [{"role": "user", "content": query}],
                "current_recipe_id": None,
                "current_step": None,
                "timer_end": None,
                "intent": "",
                "recipes": [],
            },
            config=THREAD_CONFIG,
        )
        last = result["messages"][-1]
        if last.get("role") == "assistant":
            print(f"\nОтвет: {last['content']}")
        else:
            print("\nПока умею искать рецепты. Переформулируйте запрос, например: хочу приготовить борщ.")


if __name__ == "__main__":
    main()
