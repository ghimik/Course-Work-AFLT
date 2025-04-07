import pytest
from models import DFA, State, Transition
from difference import build_difference_automaton
from util import dfa_from_string


def test_difference_basic_accepts_a_not_b():
    dfa1 = dfa_from_string({
        'states': {'s0': False, 's1': True},
        'alphabet': {'a'},
        'start': 's0',
        'transitions': {('s0', 'a'): 's1'}
    })
    dfa2 = dfa_from_string({
        'states': {'q0': False, 'q1': True},
        'alphabet': {'a'},
        'start': 'q0',
        'transitions': {('q0', 'a'): 'q1'}
    })
    diff = build_difference_automaton(dfa1, dfa2)
    # Разность должна быть пустым автоматом
    assert all(not s.is_final for s in diff.states)

def test_difference_accepts_only_in_first():
    dfa1 = dfa_from_string({
        'states': {'s0': False, 's1': True},
        'alphabet': {'a'},
        'start': 's0',
        'transitions': {('s0', 'a'): 's1'}
    })
    dfa2 = dfa_from_string({
        'states': {'q0': False, 'q1': False},
        'alphabet': {'a'},
        'start': 'q0',
        'transitions': {('q0', 'a'): 'q1'}
    })
    diff = build_difference_automaton(dfa1, dfa2)
    assert any(s.is_final for s in diff.states)



def test_difference_same_structure_different_finals():
    dfa1 = dfa_from_string({
        'states': {'s0': False, 's1': True},
        'alphabet': {'a'},
        'start': 's0',
        'transitions': {('s0', 'a'): 's1', ('s1', 'a'): 's0'}
    })
    dfa2 = dfa_from_string({
        'states': {'q0': False, 'q1': False},
        'alphabet': {'a'},
        'start': 'q0',
        'transitions': {('q0', 'a'): 'q1', ('q1', 'a'): 'q0'}
    })
    diff = build_difference_automaton(dfa1, dfa2)
    assert any(s.is_final for s in diff.states)

