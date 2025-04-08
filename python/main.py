from flask import Flask, request, jsonify
from flask_cors import CORS
from difference import build_difference_automaton, build_product_automaton
from equivalency import are_equivalent
from final_state import has_reachable_final_state
from minimize import minimize_dfa
from models import DFA, State, Transition

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

# Преобразование ДКА из JSON в объект
def dfa_from_json(data):
    """Ебучья десериализация, если структуры совпадают один в один"""
    # Обрабатываем start_state (может быть null)
    start_state_data = data.get("start_state")
    start_state = None
    if start_state_data:
        start_state = State(**start_state_data)

    # Создаем все состояния
    states = {State(**s) for s in data["states"]}

    # Создаем переходы
    transitions = {
        Transition(
            source=State(**t["source"]),
            symbol=t["symbol"],
            target=State(**t["target"])
        )
        for t in data["transitions"]
    }

    return DFA(
        states=states,
        alphabet=set(data["alphabet"]),
        transitions=transitions,
        start_state=start_state
    )

def dfa_to_json(dfa):
    return {
        "states": [{"name": state.name, "is_final": state.is_final} for state in dfa.states],
        "transitions": [{"source": t.source.name, "symbol": t.symbol, "target": t.target.name} for t in dfa.transitions],
        "alphabet": list(dfa.alphabet),
        "start_state": dfa.start_state.name
    }

# Эндпоинт минимизации ДКА
@app.route('/minimize', methods=['POST'])
def minimize():
    data = request.get_json()
    dfa = dfa_from_json(data)

    print('got dfa on min ', dfa)
    
    # Минимизируем каждый ДКА
    minimized_dfa = minimize_dfa(dfa)
    
    minimized_dfa_json = dfa_to_json(minimized_dfa)

    print("returning ", minimized_dfa_json)
    
    return jsonify(minimized_dfa_json)

# Эндпоинт проверки эквивалентности нескольких ДКА
@app.route('/equivalence', methods=['POST'])
def equivalence():
    data = request.get_json()
    
    # Преобразуем все ДКА из списка
    dfa_list = [dfa_from_json(dfa_data) for dfa_data in data]
    
    # Проверяем эквивалентность всех ДКА
    def are_all_equivalent(dfa_list):
        """Проверяет эквивалентность всех ДКА в списке с использованием логарифмической сложности.""" 
        if (len(dfa_list) == 2):
            return are_equivalent(dfa_list[0], dfa_list[1])
        elif (len(dfa_list) == 1):
            return True
        elif (len(dfa_list) == 0):
            return True
        else:
            return are_all_equivalent(dfa_list[0:len(dfa_list)/2], dfa_list[len(dfa_list)/2+1: len(dfa_list) - 1])

    try: 
        result = are_all_equivalent(dfa_list)
        print(result)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    return jsonify({"equivalent": result})


@app.route('/difference', methods=['POST'])
def difference():
    data = request.get_json()
    if len(data) != 2:
        return jsonify({"error": "Нужно передать ровно два автомата"}), 400

    dfa1 = dfa_from_json(data[0])
    dfa2 = dfa_from_json(data[1])

    result_dfa = build_difference_automaton(dfa1, dfa2)
    return jsonify(dfa_to_json(result_dfa))

@app.route('/product', methods=['POST'])
def product():
    data = request.get_json()
    if len(data) != 2:
        return jsonify({"error": "Нужно передать ровно два автомата"}), 400

    dfa1 = dfa_from_json(data[0])
    dfa2 = dfa_from_json(data[1])

    result_dfa = build_product_automaton(dfa1, dfa2)
    return jsonify(dfa_to_json(result_dfa))

# Запуск Flask-приложения
if __name__ == '__main__':
    app.run(debug=True)
