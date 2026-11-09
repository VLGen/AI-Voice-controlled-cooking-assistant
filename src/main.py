from src.agent.recipe_agent import RecipeAgent
import logging

def main():
    logging.basicConfig(level=logging.INFO)
    print("Инициализация агента...")
    agent = RecipeAgent()

    first_query = True      # Флаг первого запроса
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
        
        answer = agent.get_answer(query)
        print(f"Ответ: {answer}")

if __name__ == "__main__":
    main()