import pytest
from minimize import minimize_dfa
from models import *


def test_minimization_removes_unreachable_state():
    s0 = State("s0")
    s1 = State("s1", is_final=True)
    s2 = State("s2")  # недостижимое

    transitions = {
        Transition(s0, 'a', s1),
        Transition(s1, 'a', s0),
    }

    dfa = DFA(states={s0, s1, s2}, alphabet={'a'}, transitions=transitions, start_state=s0)
    minimized = minimize_dfa(dfa)

    state_names = {s.name for s in minimized.states}
    assert len(minimized.states) == 2
    assert "s2" not in state_names


def test_all_states_equivalent():
    s0 = State("s0", is_final=True)
    s1 = State("s1", is_final=True)
    s2 = State("s2", is_final=True)

    transitions = {
        Transition(s0, 'a', s1),
        Transition(s1, 'a', s2),
        Transition(s2, 'a', s0),
    }

    dfa = DFA(states={s0, s1, s2}, alphabet={'a'}, transitions=transitions, start_state=s0)
    minimized = minimize_dfa(dfa)

    assert len(minimized.states) == 1


def test_symmetric_but_not_equivalent():
    s0 = State("s0")
    s1 = State("s1", is_final=True)
    s2 = State("s2")
    s3 = State("s3", is_final=True)

    transitions = {
        Transition(s0, 'a', s1),
        Transition(s1, 'a', s0),
        Transition(s2, 'a', s3),
        Transition(s3, 'a', s2),
    }

    dfa = DFA(states={s0, s1, s2, s3}, alphabet={'a'}, transitions=transitions, start_state=s0)
    minimized = minimize_dfa(dfa)

    assert len(minimized.states) == 2


def test_two_identical_tails_merge():
    s0 = State("s0")
    s1 = State("s1")
    s2 = State("s2", is_final=True)
    s3 = State("s3")
    s4 = State("s4", is_final=True)

    transitions = {
        Transition(s0, 'a', s1),
        Transition(s1, 'a', s2),
        Transition(s0, 'b', s3),
        Transition(s3, 'a', s4),
    }

    dfa = DFA(states={s0, s1, s2, s3, s4}, alphabet={'a', 'b'}, transitions=transitions, start_state=s0)
    minimized = minimize_dfa(dfa)

    assert len(minimized.states) == 3


def test_already_minimized_stays_same():
    s0 = State("s0")
    s1 = State("s1", is_final=True)

    transitions = {
        Transition(s0, 'a', s1),
        Transition(s1, 'a', s0),
    }

    dfa = DFA(states={s0, s1}, alphabet={'a'}, transitions=transitions, start_state=s0)
    minimized = minimize_dfa(dfa)

    assert len(minimized.states) == 2


def test_dead_state_preserved_if_reachable():
    s0 = State("s0")
    s1 = State("s1", is_final=True)
    dead = State("dead")  # ловушка

    transitions = {
        Transition(s0, 'a', s1),
        Transition(s1, 'a', dead),
        Transition(dead, 'a', dead),
    }

    dfa = DFA(states={s0, s1, dead}, alphabet={'a'}, transitions=transitions, start_state=s0)
    minimized = minimize_dfa(dfa)

    assert len(minimized.states) == 2
    dead_states = [s for s in minimized.states if all(
        minimized.get_next_state(s, sym) == s for sym in minimized.alphabet)]
    assert len(dead_states) == 0  
