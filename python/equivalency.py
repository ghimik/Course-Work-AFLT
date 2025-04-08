
from difference import build_difference_automaton
from final_state import has_reachable_final_state
from minimize import minimize_dfa


def are_equivalent(dfa1, dfa2) -> bool:
    print("got dfas: ", dfa1, dfa2)
    minimized1 = minimize_dfa(dfa1)
    minimized2 = minimize_dfa(dfa2)

    print("minimized dfas: ", minimized1, minimized2)
    diff1 = build_difference_automaton(minimized1, minimized2)
    diff2 = build_difference_automaton(minimized2, minimized1)

    print("diff automatons: ", diff1, diff2)
    return not has_reachable_final_state(diff1) and not has_reachable_final_state(diff2)
