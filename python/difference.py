from models import DFA, State, Transition

def create_initial_state(dfa1, dfa2, state_map, queue):
    """Создаёт начальное состояние автомата разности."""
    start_pair = (dfa1.start_state, dfa2.start_state)
    if not start_pair[0] or not start_pair[1]:
        raise ValueError("В одном из автоматов отсутствует стартовое состояние!")
    new_start_state = State(f"({start_pair[0].name},{start_pair[1].name})")
    state_map[start_pair] = new_start_state
    queue.append(start_pair)
    return new_start_state

def process_state_pairs(dfa1, dfa2, state_map, queue, new_transitions):
    """Обрабатывает пары состояний и создаёт переходы."""
    new_states = set()

    while queue:
        q1, q2 = queue.pop(0)
        new_state = state_map[(q1, q2)]
        new_states.add(new_state)

        for symbol in dfa1.alphabet.union(dfa2.alphabet):
            next_q1 = dfa1.get_next_state(q1, symbol)
            next_q2 = dfa2.get_next_state(q2, symbol)

            # если нет перехода — уходим в "поглощающее состояние"
            next_q1 = next_q1 if next_q1 else State("⊥1", is_final=False)
            next_q2 = next_q2 if next_q2 else State("⊥2", is_final=False)

            next_pair = (next_q1, next_q2)

            if next_pair not in state_map:
                new_state_name = f"({next_q1.name},{next_q2.name})"
                state_map[next_pair] = State(new_state_name)
                queue.append(next_pair)

            new_transitions.add(Transition(new_state, symbol, state_map[next_pair]))

    return new_states


def mark_difference_final_states(state_map):
    """Отмечает финальные состояния в автомате разности A - B."""
    for (q1, q2), new_state in state_map.items():
        if q1.is_final and not q2.is_final:
            new_state.is_final = True


def mark_product_final_states(state_map):
    """Отмечает финальные состояния в автомате произведения A х B."""
    for (q1, q2), new_state in state_map.items():
        if q1.is_final and not q2.is_final:
            new_state.is_final = True


def build_product_automaton(dfa1: DFA, dfa2: DFA) -> DFA:
    """Создаёт автомат разности для двух ДКА."""
    new_transitions = set()
    state_map = {}
    queue = []

    new_start_state = create_initial_state(dfa1, dfa2, state_map, queue)
    new_states = process_state_pairs(dfa1, dfa2, state_map, queue, new_transitions)
    mark_product_final_states(state_map)

    return DFA(set(state_map.values()), dfa1.alphabet.union(dfa2.alphabet), new_transitions, new_start_state)


def build_difference_automaton(dfa1: DFA, dfa2: DFA) -> DFA:
    """Создаёт автомат разности для двух ДКА."""
    new_transitions = set()
    state_map = {}
    queue = []

    new_start_state = create_initial_state(dfa1, dfa2, state_map, queue)
    new_states = process_state_pairs(dfa1, dfa2, state_map, queue, new_transitions)
    mark_difference_final_states(state_map)

    return DFA(set(state_map.values()), dfa1.alphabet.union(dfa2.alphabet), new_transitions, new_start_state)
