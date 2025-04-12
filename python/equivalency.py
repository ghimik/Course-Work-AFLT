
from difference import build_difference_automaton
from final_state import has_reachable_final_state
from minimize import minimize_dfa
from models import DFA


def are_equivalent(dfa1: DFA, dfa2: DFA) -> bool:
    """Проверяет эквивалентность двух ДКА."""
    # Проверка на пустые автоматы
    if not dfa1.start_state and not dfa2.start_state:
        return True  # Два пустых автомата эквивалентны
    if not dfa1.start_state or not dfa2.start_state:
        return False  # Один из автоматов пустой, другой — нет

    # Минимизация автоматов
    minimized_dfa1 = minimize_dfa(dfa1)
    minimized_dfa2 = minimize_dfa(dfa2)

    # Строим автомат разности A - B
    diff_ab = build_difference_automaton(minimized_dfa1, minimized_dfa2)
    if has_reachable_final_state(diff_ab):
        return False  # Найдено слово, которое принимает первый автомат, но не второй

    # Строим автомат разности B - A
    diff_ba = build_difference_automaton(minimized_dfa2, minimized_dfa1)
    if has_reachable_final_state(diff_ba):
        return False  # Найдено слово, которое принимает второй автомат, но не первый

    return True  # Автоматы эквивалентны