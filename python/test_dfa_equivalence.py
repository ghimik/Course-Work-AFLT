from equivalency import are_equivalent
from final_state import has_reachable_final_state
import pytest
from models import State, Transition, DFA
from difference import build_difference_automaton
from minimize import minimize_dfa
from util import dfa_from_string

def make_dfa_1():
    # Простой ДКА, распознающий язык a*
    q0 = State("q0", is_final=True)
    transitions = {
        Transition(q0, "a", q0),
    }
    return DFA({q0}, {"a"}, transitions, q0)


def make_dfa_2():
    # Эквивалентный DFA (другим способом)
    q0 = State("s0", is_final=True)
    q1 = State("s1", is_final=False)  # unreachable
    transitions = {
        Transition(q0, "a", q0),
        Transition(q1, "a", q1),
    }
    return DFA({q0, q1}, {"a"}, transitions, q0)


def make_dfa_non_eq():
    # DFA, распознающий язык a*a (не эквивалентен a*)
    q0 = State("q0", is_final=False)
    q1 = State("q1", is_final=True)
    transitions = {
        Transition(q0, "a", q1),
        Transition(q1, "a", q1),
    }
    return DFA({q0, q1}, {"a"}, transitions, q0)


def make_dfa_min_test():
    # Неприменённый DFA, эквивалентен a*
    q0 = State("A", is_final=True)
    q1 = State("B", is_final=True)
    transitions = {
        Transition(q0, "a", q1),
        Transition(q1, "a", q0),
    }
    return DFA({q0, q1}, {"a"}, transitions, q0)


def test_equivalent_simple():
    dfa1 = make_dfa_1()
    dfa2 = make_dfa_2()
    assert are_equivalent(dfa1, dfa2)


def test_non_equivalent():
    dfa1 = make_dfa_1()
    dfa3 = make_dfa_non_eq()
    assert not are_equivalent(dfa1, dfa3)


def test_equivalent_after_minimization():
    dfa1 = make_dfa_1()
    dfa4 = make_dfa_min_test()
    dfa4_min = minimize_dfa(dfa4)
    assert are_equivalent(dfa1, dfa4_min)


def test_minimized_vs_original_equivalent():
    dfa = make_dfa_non_eq()
    minimized = minimize_dfa(dfa)
    assert are_equivalent(dfa, minimized)

def test_identical_automata_with_unused_symbol():
    # Создаём два одинаковых автомата, но один имеет лишний символ в алфавите
    dfa1 = dfa_from_string({
        'states': {'s0': False, 's1': True},
        'alphabet': {'a'},  # Только символ 'a' в алфавите
        'start': 's0',
        'transitions': {('s0', 'a'): 's1', ('s1', 'a'): 's0'}
    })

    dfa2 = dfa_from_string({
        'states': {'s0': False, 's1': True},
        'alphabet': {'a', 'b'},  # Добавлен лишний символ 'b'
        'start': 's0',
        'transitions': {('s0', 'a'): 's1', ('s1', 'a'): 's0'}
    })
    
    # Проверяем эквивалентность до минимизации
    assert are_equivalent(dfa1, dfa2), "Automata should be equivalent"

    # Минимизируем оба автомата
    minimized_dfa1 = minimize_dfa(dfa1)
    minimized_dfa2 = minimize_dfa(dfa2)

    # Проверяем эквивалентность после минимизации
    assert are_equivalent(minimized_dfa1, minimized_dfa2), "Minimized automata should be equivalent"

    # Проверяем, что лишний символ 'b' был удалён в процессе минимизации (если это нужно)
    # assert 'b' not in minimized_dfa1.alphabet_
