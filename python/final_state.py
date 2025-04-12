from models import DFA
from util import bfs

def has_reachable_final_state(dfa: DFA) -> bool:
    """Проверяет, достижимо ли хотя бы одно финальное состояние в ДКА."""
    if dfa.start_state is None:
        return False 
    
    return bfs(
        start=dfa.start_state,
        is_goal=lambda state: state.is_final,
        get_neighbors=lambda state: [dfa.get_next_state(state, symbol) for symbol in dfa.alphabet]
    )
