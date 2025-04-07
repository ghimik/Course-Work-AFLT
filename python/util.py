from collections import deque

from models import DFA, State, Transition

def bfs(start, is_goal, get_neighbors):
    """
    Универсальный BFS-обход.
    
    :param start: Начальная вершина.
    :param is_goal: Функция, проверяющая, является ли вершина целевой.
    :param get_neighbors: Функция, возвращающая соседей вершины.
    :return: True, если найдена целевая вершина, иначе False.
    """
    visited = set()
    queue = deque([start])

    while queue:
        current = queue.popleft()

        if is_goal(current):
            return True  # Нашли целевую вершину!

        if current in visited:
            continue
        visited.add(current)

        for neighbor in get_neighbors(current):
            if neighbor and neighbor not in visited:
                queue.append(neighbor)

    return False  # Целевая вершина недостижима


def dfa_from_string(description):
    """Быстро собираем DFA по описанию"""
    states = {}
    transitions = set()
    for name, final in description['states'].items():
        states[name] = State(name, is_final=final)
    for (from_, symbol), to in description['transitions'].items():
        transitions.add(Transition(states[from_], symbol, states[to]))
    return DFA(
        states=set(states.values()),
        alphabet=description['alphabet'],
        transitions=transitions,
        start_state=states[description['start']]
    )