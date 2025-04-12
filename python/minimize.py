from collections import defaultdict

from models import DFA, State, Transition
def find_partition(state, partitions):
    """Находит индекс класса разбиения для состояния."""
    for idx, part in enumerate(partitions):
        if state in part:
            return idx  # индекс, а не сам set
    return None

def refine_partitions(dfa, partitions):
    """Итеративно уточняет разбиение состояний с учетом переходов и финальности."""
    while True:
        new_partitions = []
        for part in partitions:
            groups = defaultdict(set)
            for state in part:
                signature = tuple(
                    (find_partition(dfa.get_next_state(state, symbol), partitions)) 
                    for symbol in dfa.alphabet
                )
                groups[signature].add(state)
            new_partitions.extend(groups.values())

        if new_partitions == partitions:
            return partitions  # Разбиение стабилизировалось
        partitions = new_partitions



def build_minimized_dfa(dfa, partitions):
    """Создаёт новый минимизированный ДКА на основе разбиения."""
    index_to_part = {idx: frozenset(part) for idx, part in enumerate(partitions)}
    new_states = {
        part: State(f"Q{idx}", any(s.is_final for s in part))
        for idx, part in index_to_part.items()
    }
    new_transitions = set()


    for part, new_state in new_states.items():
        for symbol in dfa.alphabet:
            old_state = next(iter(part))  # Берём любое состояние из класса
            next_old_state = dfa.get_next_state(old_state, symbol)
            if next_old_state:
                target_partition_index = find_partition(next_old_state, partitions)
                target_partition = index_to_part[target_partition_index]
                next_new_state = new_states[target_partition]
                new_transitions.add(Transition(new_state, symbol, next_new_state))

    new_start_state = new_states[index_to_part[find_partition(dfa.start_state, partitions)]]
    return DFA(set(new_states.values()), dfa.alphabet, new_transitions, new_start_state)


def minimize_dfa(dfa: DFA) -> DFA:
    """Минимизирует ДКА с помощью алгоритма Хопкрофта."""
    
    final_states = {s for s in dfa.states if s.is_final}
    dfa = remove_unreachable_states(dfa) 
    final_states = {s for s in dfa.states if s.is_final}
    dfa = remove_dead_states(dfa)

    if not dfa.transitions:
        # Если нет переходов, то автомат может быть либо пустым, либо состоять из одного состояния
        if dfa.start_state.is_final:
            # Если стартовое состояние также является финальным, создаем ДКА с одним состоянием
            single_state = State(name="q0", is_final=True)
            return DFA(
                states={single_state},
                alphabet=set(),
                transitions=set(),
                start_state=single_state
            )
        else:
            # В противном случае возвращаем пустой ДКА
            return DFA(
                states=set(),
                alphabet=set(),
                transitions=set(),
                start_state=None
            )

    non_final_states = dfa.states - final_states
    partitions = refine_partitions(dfa, [final_states, non_final_states])
    return build_minimized_dfa(dfa, partitions)


def remove_unreachable_states(dfa: DFA) -> DFA:
    reachable = set()
    frontier = {dfa.start_state}

    while frontier:
        state = frontier.pop()
        if state not in reachable:
            reachable.add(state)
            for symbol in dfa.alphabet:
                next_state = dfa.get_next_state(state, symbol)
                if next_state:
                    frontier.add(next_state)


    reachable_transitions = {t for t in dfa.transitions if t.source in reachable and t.target in reachable}
    return DFA(states=reachable, alphabet=dfa.alphabet, transitions=reachable_transitions, start_state=dfa.start_state)

def remove_dead_states(dfa: DFA) -> DFA:
    """Удаляет мертвые состояния — те, из которых нельзя попасть в финальное состояние."""
    reverse_graph = defaultdict(set)

    # Построим обратный граф
    for t in dfa.transitions:
        reverse_graph[t.target].add((t.source, t.symbol))

    # Начнем поиск из финальных состояний
    alive = set()
    frontier = {s for s in dfa.states if s.is_final}

    while frontier:
        state = frontier.pop()
        if state not in alive:
            alive.add(state)
            for prev_state, _ in reverse_graph[state]:
                frontier.add(prev_state)

    # Фильтруем состояния и переходы
    alive_transitions = {t for t in dfa.transitions if t.source in alive and t.target in alive}
    return DFA(states=alive, alphabet=dfa.alphabet, transitions=alive_transitions, start_state=dfa.start_state)
