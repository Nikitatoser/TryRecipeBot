from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

# Инициализация модели
model = ChatOllama(
    model="gemma2:9b",
    temperature=0.9,
)

# Определение структуры данных
class Recipe(BaseModel):
    title: str = Field(description="Title of the recipe")
    ingredients: list[str] = Field(description="List of ingredients")
    instructions: list[str] = Field(description="Preparation instructions")

def generate_recipe(ingredients: str, cuisine: str, language: str):
    parser = JsonOutputParser(pydantic_object=Recipe)
    prompt_template_name = PromptTemplate(
    input_variables=["ingredients", "cuisine", "language"],
    template = (
        "I want to generate a recipe based on the ingredients I have available in a structured format. "
        "You can use existing recipes that include some or all of my ingredients and adapt them to fit the available ones. "
        "Please follow these steps to provide the recipe:\n"
        "1. Provide a creative and descriptive title for the dish based on the ingredients and cuisine.\n"
        "2. List all the ingredients in a bullet-point format, including quantities and specific measurements.\n"
        "3. Write clear, easy-to-follow step-by-step instructions for preparing the dish. "
        "   Ensure the steps are logical and include necessary details like cooking times, temperatures, and techniques.\n"
        "4. Provide additional tips or variations, if applicable.\n"
        "5. Ensure the recipe is relevant to the specified cuisine, reflecting its authentic flavors and ingredients.\n"
        "Answer only in JSON format with the following fields: title, ingredients, instructions, tips (optional).\n"
        "Make sure to provide the response in {language} but keep the JSON tags in English.\n"
        "For reference, here is the data you are working with:\n"
        "Ingredients: {ingredients}\n"
        "Cuisine: {cuisine}\n"
        "Please follow the format strictly, and include {format_instructions}."
    ),
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # Создание цепочки
    chain = prompt_template_name | model | parser

    try:
        result = chain.invoke({"ingredients": ingredients, "cuisine": cuisine, "language": language})
        return result
    except Exception as e:
        print("Error:", e)


