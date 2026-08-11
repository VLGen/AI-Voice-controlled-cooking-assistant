from llm.llm_generator import LLMGenerator

def test_generation():
    print("Инициализация генератора...")
    generator = LLMGenerator()
    print("\n" + "="*50)
    
    # Тестовые данные
    test_cases = [
        {"recipe": "паста карбонара"},
        {"recipe": "пышный омлет"},
        {"recipe": "гречка с курицей"}
    ]
    
    for case in test_cases:
        print(f"\n--- Блюдо: {case['recipe']} ---")
        intro = generator.generate_intro(case['recipe'])
        print(f"Интро: {intro}")
        
        congrats = generator.generate_congratulation(case['recipe'])
        print(f"Поздравление: {congrats}")
        print("-"*30)

if __name__ == "__main__":
    test_generation()