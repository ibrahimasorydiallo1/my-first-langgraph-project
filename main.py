from typing import Annotated, List, Literal
from pydantic import BaseModel
from operator import add
from pyjokes import get_joke
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph


class Joke(BaseModel):
    text: str
    category: str

class JokeState(BaseModel):
    jokes: Annotated[List[Joke], add] = []
    jokes_choice: Literal["p", "c", "q"] = "p" # prochaine blague, changer de catégorie, quitter
    category: str = "neutral"
    language: str = "fr"
    quit: bool = False


def show_menu(state: JokeState) -> dict:
    """Cette fonction affiche le menu et récupère le choix de l'utilisateur."""

    try:
        user_input = input("[p] Prochaine  [c] Changer de catégorie  [q] Quitter\n> ").strip().lower()
    except ValueError:
        print("Sélection invalide, retour à la catégorie par défaut.")
        user_input = "p"

    return {"jokes_choice": user_input}


def fetch_joke(state: JokeState) -> dict:
    """Cette fonction récupère les blagues à partir de la librairie pyjokes."""

    joke_text = get_joke(language=state.language, category=state.category)
    new_joke = Joke(text=joke_text, category=state.category)
    print(f"\nVoici une blague ({state.category}): {joke_text}\n")

    return {"jokes": [new_joke]}


def update_category(state: JokeState) -> dict:
    """Cette fonction permet de changer la catégorie des blagues."""

    categories = ["neutral", "all"]
    try:
        selection = int(input("Selectionne la catégorie [0=neutral, 1=all]: ").strip())
    except ValueError:
        print("Sélection invalide, retour à la catégorie par défaut.")
        selection = 0

    return {"category": categories[selection]}


def exit_bot(state: JokeState) -> dict:
    return {"Quitter": True}


def route_choice(state: JokeState) -> str:
    """Définissons la logique de routage en fonction du choix de l'utilisateur."""

    if state.jokes_choice == "p":
        return "fetch_joke"
    elif state.jokes_choice == "c":
        return "update_category"
    elif state.jokes_choice == "q":
        return "exit_bot"
    return "exit_bot"


def build_joke_graph() -> CompiledStateGraph:
    """Création du graphe, définition de la structure du workflow et sauvegarde des nodes créés."""

    workflow = StateGraph(JokeState)

    workflow.add_node("show_menu", show_menu)
    workflow.add_node("fetch_joke", fetch_joke)
    workflow.add_node("update_category", update_category)
    workflow.add_node("exit_bot", exit_bot)

    workflow.set_entry_point("show_menu")

    workflow.add_conditional_edges(
        "show_menu",
        route_choice,
        {
            "fetch_joke": "fetch_joke",
            "update_category": "update_category",
            "exit_bot": "exit_bot",
        },
    )

    workflow.add_edge("fetch_joke", "show_menu")
    workflow.add_edge("update_category", "show_menu")
    workflow.add_edge("exit_bot", END)

    return workflow.compile()


def main():
    graph = build_joke_graph()
    try:
        final_state = graph.invoke(JokeState(), config={"recursion_limit": 18})
    except Exception as e:
        print(f"Vous avez atteint la limite. Revenez plus tard !")

if __name__ == "__main__":
    main()
