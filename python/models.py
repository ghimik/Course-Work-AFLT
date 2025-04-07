class State:
    def __init__(self, name: str, is_final: bool = False):
        self.name = name
        self.is_final = is_final

    def __repr__(self):
        return f"State({self.name}, final={self.is_final})"

    def __eq__(self, other):
        return isinstance(other, State) and self.name == other.name and self.is_final == other.is_final

    def __hash__(self):
        return hash((self.name, self.is_final))


class Transition:
    def __init__(self, from_state: State, symbol: str, to_state: State):
        self.from_state = from_state
        self.symbol = symbol
        self.to_state = to_state

    def __repr__(self):
        return f"Transition({self.from_state} --{self.symbol}--> {self.to_state})"

    def __eq__(self, other):
        return (
            isinstance(other, Transition) and
            self.from_state == other.from_state and
            self.symbol == other.symbol and
            self.to_state == other.to_state
        )

    def __hash__(self):
        return hash((self.from_state, self.symbol, self.to_state))


class DFA:
    def __init__(self, states: set[State], alphabet: set[str], transitions: set[Transition], start_state: State):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.transition_dict = self._build_transition_dict()

    def _build_transition_dict(self):
        """Создаёт удобную структуру данных для быстрого доступа к переходам."""
        transition_dict = {}
        for t in self.transitions:
            transition_dict[(t.from_state, t.symbol)] = t.to_state
        return transition_dict

    def get_next_state(self, current_state: State, symbol: str) -> State | None:
        """Возвращает следующее состояние по символу или None, если перехода нет."""
        return self.transition_dict.get((current_state, symbol))
    
    def check_word(self, word: str) -> bool:
        """Проверяет, принадлежит ли слово языку, который распознаёт ДКА."""
        current_state = self.start_state
        for symbol in word:
            current_state = self.get_next_state(current_state, symbol)
            if current_state is None:  # Нет перехода по символу
                return False
        return current_state.is_final  # Проверяем, финальное ли состояние


    def __repr__(self):
        return f"DFA(states={self.states}, alphabet={self.alphabet}, start_state={self.start_state})"
