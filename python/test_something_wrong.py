import pytest
from difference import build_difference_automaton
from models import DFA, State, Transition


def make_dfa_ab_star():
    # Язык: a*b
    s0 = State("q0", is_final=False)
    s1 = State("q1", is_final=True)

    transitions = {
        Transition(s0, "a", s0),
        Transition(s0, "b", s1),
    }

    return DFA(states={s0, s1}, alphabet={"a", "b"}, transitions=transitions, start_state=s0)


def make_dfa_a_plus_b_plus():
    # Язык: a+b+
    s0 = State("q0", is_final=False)
    s1 = State("q1", is_final=False)
    s2 = State("q2", is_final=True)

    transitions = {
        Transition(s0, "a", s1),
        Transition(s1, "a", s1),
        Transition(s1, "b", s2),
        Transition(s2, "b", s2),
    }

    return DFA(states={s0, s1, s2}, alphabet={"a", "b"}, transitions=transitions, start_state=s0)


def make_empty_dfa():
    # Язык пустой (∅)
    s0 = State("q0", is_final=False)
    return DFA(states={s0}, alphabet={"a", "b"}, transitions=set(), start_state=s0)


def test_difference_basic_language():
    dfa1 = make_dfa_ab_star()
    dfa2 = make_dfa_a_plus_b_plus()

    diff = build_difference_automaton(dfa1, dfa2)
    assert diff.check_word("b") is True
    assert diff.check_word("ab") is False
    assert diff.check_word("aab") is False


def test_difference_same_dfa():
    dfa = make_dfa_ab_star()
    diff = build_difference_automaton(dfa, dfa)
    assert all(not s.is_final for s in diff.states)
    assert diff.check_word("b") is False
    assert diff.check_word("ab") is False


def test_difference_with_empty_b():
    dfa = make_dfa_ab_star()
    empty = make_empty_dfa()
    diff = build_difference_automaton(dfa, empty)

    assert diff.check_word("b") is True
    assert diff.check_word("ab") is True
    assert diff.check_word("aab") is True


def test_difference_empty_minus_something():
    dfa = make_dfa_ab_star()
    empty = make_empty_dfa()
    diff = build_difference_automaton(empty, dfa)

    assert all(not s.is_final for s in diff.states)
    assert diff.check_word("b") is False
    assert diff.check_word("ab") is False
