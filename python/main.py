from flask import Flask, request, jsonify
from flask_cors import CORS
from difference import build_difference_automaton
from final_state import has_reachable_final_state
from minimize import minimize_dfa
from models import DFA, State, Transition
from util import bfs

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

# Преобразование ДКА из JSON в объект
def dfa_from_json(data):
    """Преобразует JSON в объект DFA."""
    states = {State(state["name"], state.get("is_final", False)) for state in data["states"]}
    transitions = {
        Transition(State(t["from"]), t["symbol"], State(t["to"])) for t in data["transitions"]
    }
    alphabet = set(data["alphabet"])
    start_state = next(state for state in states if state.name == data["start_state"])
    return DFA(states, alphabet, transitions, start_state)

# Эндпоинт минимизации ДКА
@app.route('/minimize', methods=['POST'])
def minimize():
    data = request.get_json()
    dfa_list = [dfa_from_json(dfa_data) for dfa_data in data]
    
    # Минимизируем каждый ДКА
    minimized_dfas = [minimize_dfa(dfa) for dfa in dfa_list]
    
    minimized_dfa_jsons = [{
        "states": [{"name": state.name, "is_final": state.is_final} for state in minimized_dfa.states],
        "transitions": [{"from": t.from_state.name, "symbol": t.symbol, "to": t.to_state.name} for t in minimized_dfa.transitions],
        "alphabet": list(minimized_dfa.alphabet),
        "start_state": minimized_dfa.start_state.name
    } for minimized_dfa in minimized_dfas]
    
    return jsonify(minimized_dfa_jsons)

# Эндпоинт проверки эквивалентности нескольких ДКА
@app.route('/equivalence', methods=['POST'])
def equivalence():
    data = request.get_json()
    
    # Преобразуем все ДКА из списка
    dfa_list = [dfa_from_json(dfa_data) for dfa_data in data]
    
    # Проверяем эквивалентность всех ДКА
    def are_all_equivalent(dfa_list):
        """Проверяет эквивалентность всех ДКА в списке с использованием логарифмической сложности.""" 
        # Сначала сравниваем пары 1-2, 3-4, 5-6, 7-8 и т.д.
        groups = [(dfa_list[i], dfa_list[i + 1]) for i in range(0, len(dfa_list), 2)]
        
        # Пока группы не сойдутся в одно множество
        while len(groups) > 1:
            next_groups = []
            for i in range(0, len(groups), 2):
                if i + 1 < len(groups):
                    dfa1, dfa2 = groups[i]
                    dfa3, dfa4 = groups[i + 1]
                    # Проверяем пару из двух групп (1-2 и 3-4)
                    diff_automaton = build_difference_automaton(dfa1, dfa4)
                    if has_reachable_final_state(diff_automaton):
                        return False
                    next_groups.append((dfa1, dfa4))
                else:
                    next_groups.append(groups[i])
            groups = next_groups
        
        # В конце возвращаем True, если все группы эквивалентны
        return True


    result = are_all_equivalent(dfa_list)
    return jsonify({"equivalent": result})

# Запуск Flask-приложения
if __name__ == '__main__':
    app.run(debug=True)
