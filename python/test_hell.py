import pytest
from equivalency import are_equivalent
from models import *

def make_empty_dfa():
    """Генератор пустого автомата (не принимающий язык)."""
    start_state = State("q0", is_final=False)
    return DFA(
        states={start_state},
        alphabet=set(),
        start_state=start_state,
        transitions=set()
    )

def make_dfa_ab_star():
    """Генератор ДКА, принимающего (ab)*."""
    q0 = State("q0", is_final=True)
    q1 = State("q1", is_final=False)
    q2 = State("q2", is_final=True)
    
    transitions = {
        Transition(q0, 'a', q1),
        Transition(q1, 'b', q2),
        Transition(q2, 'a', q1),
        Transition(q1, 'b', q0)
    }
    
    return DFA(
        states={q0, q1, q2},
        alphabet={'a', 'b'},
        start_state=q0,
        transitions=transitions
    )

def make_dfa_ab_star_smart():
    """Генератор хитрого эквивалентного автомата для (ab)* с дополнительными переходами и состояниями."""
    q0 = State("q0", is_final=True)
    q1 = State("q1", is_final=False)
    q2 = State("q2", is_final=True)
    q3 = State("q3", is_final=False)

    transitions = {
        Transition(q0, 'a', q1),
        Transition(q1, 'b', q2),
        Transition(q2, 'a', q1),
        Transition(q1, 'b', q0),
        Transition(q0, 'a', q3),  # Ложный путь, который не будет использоваться
        Transition(q3, 'b', q2),   # Ложный путь, который также не будет использоваться
        Transition(q2, 'a', q3),   # Ложный переход, возвращающий в "лишнее" состояние
        Transition(q3, 'b', q0),   # Ложный цикл, снова возвращаемся к начальной точке
    }

    return DFA(
        states={q0, q1, q2, q3},
        alphabet={'a', 'b'},
        start_state=q0,
        transitions=transitions
    )


def make_dfa_a_star_b_star():
    """Генератор ДКА, принимающего a*b*."""
    q0 = State("q0", is_final=True)
    q1 = State("q1", is_final=False)
    q2 = State("q2", is_final=True)

    transitions = {
        Transition(q0, 'a', q1),
        Transition(q1, 'a', q1),
        Transition(q1, 'b', q2),
        Transition(q2, 'b', q2)
    }
    
    return DFA(
        states={q0, q1, q2},
        alphabet={'a', 'b'},
        start_state=q0,
        transitions=transitions
    )

def make_dfa_a_star_b_plus():
    """Генератор ДКА, принимающего a*b+."""
    q0 = State("q0", is_final=False)
    q1 = State("q1", is_final=True)
    q2 = State("q2", is_final=False)

    transitions = {
        Transition(q0, 'a', q1),
        Transition(q1, 'a', q1),
        Transition(q1, 'b', q2),
        Transition(q2, 'b', q2)
    }
    
    return DFA(
        states={q0, q1, q2},
        alphabet={'a', 'b'},
        start_state=q0,
        transitions=transitions
    )

def make_dfa_with_unreachable_is_final_state():
    """Генератор автомата с недостижимым финальным состоянием."""
    q0 = State("q0", is_final=False)
    q1 = State("q1", is_final=True)
    
    transitions = {
        Transition(q0, 'a', q0),
        Transition(q0, 'b', q0)
    }

    return DFA(
        states={q0, q1},
        alphabet={'a', 'b'},
        start_state=q0,
        transitions=transitions
    )

def make_dfa_only_accepts_a_cycle():
    """Генератор автомата, принимающего только цикл по 'a'."""
    q0 = State("q0", is_final=False)
    q1 = State("q1", is_final=True)

    transitions = {
        Transition(q0, 'a', q1),
        Transition(q1, 'a', q1)
    }
    
    return DFA(
        states={q0, q1},
        alphabet={'a'},
        start_state=q0,
        transitions=transitions
    )

def make_dead_loop_dfa():
    """Генератор ДКА с мертвым циклом (всё возвращается к себе, но нет финальных состояний)."""
    q0 = State("q0", is_final=False)
    q1 = State("q1", is_final=False)

    transitions = {
        Transition(q0, 'a', q0),
        Transition(q0, 'b', q1),
        Transition(q1, 'a', q1),
        Transition(q1, 'b', q1)
    }
    
    return DFA(
        states={q0, q1},
        alphabet={'a', 'b'},
        start_state=q0,
        transitions=transitions
    )

def make_dfa_ab_star_with_extra_symbols():
    """Генератор ДКА с алфавитом {'a', 'b', 'c'}, но принимающий только (ab)*."""
    q0 = State("q0", is_final=True)
    q1 = State("q1", is_final=False)
    q2 = State("q2", is_final=True)
    
    transitions = {
        Transition(q0, 'a', q1),
        Transition(q1, 'b', q2),
        Transition(q2, 'a', q1),
        Transition(q1, 'b', q0)
    }
    
    return DFA(
        states={q0, q1, q2},
        alphabet={'a', 'b', 'c'},
        start_state=q0,
        transitions=transitions
    )

def make_dfa_a_star_with_b_as_dead_state():
    """Генератор ДКА с алфавитом {'a', 'b'}, где b — мёртвое состояние."""
    q0 = State("q0", is_final=True)
    q1 = State("q1", is_final=False)
    
    transitions = {
        Transition(q0, 'a', q1),
        Transition(q1, 'a', q1),
        Transition(q0, 'b', q1),
        Transition(q1, 'b', q1)
    }
    
    return DFA(
        states={q0, q1},
        alphabet={'a', 'b'},
        start_state=q0,
        transitions=transitions
    )

def make_dfa_accepts_even_length_words():
    """Генератор ДКА, принимающего только четные длины слов."""
    q0 = State("q0", is_final=True)
    q1 = State("q1", is_final=False)
    
    transitions = {
        Transition(q0, 'a', q1),
        Transition(q1, 'a', q0),
        Transition(q0, 'b', q1),
        Transition(q1, 'b', q0)
    }

    return DFA(
        states={q0, q1},
        alphabet={'a', 'b'},
        start_state=q0,
        transitions=transitions
    )

def make_dfa_accepts_even_length_words_with_extra_states():
    """Генератор ДКА, принимающего четные длины слов, но с дополнительными состояниями."""
    q0 = State("q0", is_final=True)
    q1 = State("q1", is_final=False)
    q2 = State("q2", is_final=False)
    
    transitions = {
        Transition(q0, 'a', q1),
        Transition(q1, 'a', q0),
        Transition(q0, 'b', q1),
        Transition(q1, 'b', q0),
        Transition(q2, 'a', q0),  # лишние переходы
        Transition(q2, 'b', q1)   # лишние переходы
    }

    return DFA(
        states={q0, q1, q2},
        alphabet={'a', 'b'},
        start_state=q0,
        transitions=transitions
    )


def test_empty_vs_empty_equivalent():
    dfa1 = make_empty_dfa()
    dfa2 = make_empty_dfa()
    assert are_equivalent(dfa1, dfa2)

def test_empty_vs_nonempty_not_equivalent():
    dfa1 = make_empty_dfa()
    dfa2 = make_dfa_ab_star()
    assert not are_equivalent(dfa1, dfa2)

def test_same_language_different_structure_equivalent():
    dfa1 = make_dfa_ab_star()  # принимает (ab)*
    dfa2 = make_dfa_ab_star_smart()  # тот же язык, другой граф
    assert are_equivalent(dfa1, dfa2)


def test_similar_but_not_equivalent():
    dfa1 = make_dfa_a_star_b_star()
    dfa2 = make_dfa_a_star_b_plus()
    assert not are_equivalent(dfa1, dfa2)


def test_unreachable_is_final_state():
    dfa1 = make_dfa_with_unreachable_is_final_state()
    dfa2 = make_empty_dfa()
    assert are_equivalent(dfa1, dfa2)


def test_dead_loop_vs_empty():
    dfa1 = make_dead_loop_dfa()  # всё возвращается к себе, но нет финальных
    dfa2 = make_empty_dfa()
    assert are_equivalent(dfa1, dfa2)

def test_different_alphabets_equivalent_by_intersection():
    dfa1 = make_dfa_ab_star()
    dfa2 = make_dfa_ab_star_with_extra_symbols()  # ещё 'c', но c не используется
    assert are_equivalent(dfa1, dfa2)


def test_equivalent_via_different_paths():
    dfa1 = make_dfa_accepts_even_length_words()
    dfa2 = make_dfa_accepts_even_length_words_with_extra_states()
    assert are_equivalent(dfa1, dfa2)
