CREATE_EXTENSION = """
    CREATE EXTENSION IF NOT EXISTS vector;
"""

# Таблица с рецептами
CREATE_RECIPES_TABLE = """
    CREATE TABLE IF NOT EXISTS recipes (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        link TEXT,
        cooking_time_minutes INT,
        kitchen TEXT,
        servings INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        embedding vector(1024)
    );
"""

# Таблица с ингредиентами
CREATE_INGREDIENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS ingredients (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    );
"""

# Таблица с ингредиентами конкретного рецепта
CREATE_RECIPE_INGREDIENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS recipe_ingredients (
        id SERIAL PRIMARY KEY,
        ingredient_id INT REFERENCES ingredients(id) ON DELETE CASCADE,
        recipe_id INT REFERENCES recipes(id) ON DELETE CASCADE,
        amount TEXT,
        unit TEXT
    );
"""

# Таблица с описанием и нумирацией шагов
CREATE_STEPS_TABLE = """
    CREATE TABLE IF NOT EXISTS steps(
        id SERIAL PRIMARY KEY,
        recipe_id INT REFERENCES recipes(id) ON DELETE CASCADE,
        step_number INT,
        instruction TEXT,
        duration_minutes INT,
        UNIQUE (recipe_id, step_number)
    );
"""