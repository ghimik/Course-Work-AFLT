import argparse
import json
from typing import Optional

from difference import build_difference_automaton, build_product_automaton
from equivalency import are_equivalent
from minimize import minimize_dfa
from models import *

def dfa_from_json(data):
    """Полное чтение, десериализация объектов через JSON"""
    start_state_data = data.get("start_state")
    start_state = None
    if start_state_data:
        start_state = State(**start_state_data)

    states = {State(**s) for s in data["states"]}
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

def dfa_from_string(description):
    """Сокращённое чтение, быстрое создание DFA по описанию"""
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

def load_dfa(file_path: Optional[str], input_str: Optional[str], full: bool):
    """Загружает DFA из файла или строки, в зависимости от флага full"""
    if input_str:
        description = json.loads(input_str)
        return dfa_from_json(description) if full else dfa_from_string(description)
    elif file_path:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return dfa_from_json(data) if full else dfa_from_string(data)
    else:
        raise ValueError("Не указан источник данных")

def write_dfa(dfa: DFA, full: bool, output_file: Optional[str] = None):
    """Запись DFA в файл или в консоль"""
    data = dfa_to_dict(dfa, full)
    output = json.dumps(data, indent=2)
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output)
    else:
        print(output)

def dfa_to_dict(dfa: DFA, full: bool):
    """Преобразование DFA в словарь для вывода"""
    if full:
        return {
            "states": [state.to_dict() for state in dfa.states],
            "alphabet": list(dfa.alphabet),
            "transitions": [{
                "source": t.source.to_dict(),
                "symbol": t.symbol,
                "target": t.target.to_dict()
            } for t in dfa.transitions],
            "start_state": dfa.start_state.to_dict() if dfa.start_state else None
        }
    else:
        return {
            "states": {state.name: state.is_final for state in dfa.states},
            "alphabet": list(dfa.alphabet),
            "transitions": {(t.source.name, t.symbol): t.target.name for t in dfa.transitions},
            "start": dfa.start_state.name if dfa.start_state else None
        }

def main():
    parser = argparse.ArgumentParser(description="CLI утилита для работы с ДКА")
    parser.add_argument('--input', type=str, help="Входные данные как строка JSON")
    parser.add_argument('--input-file', type=str, help="Файл с входными данными")
    parser.add_argument('--output-file', type=str, help="Файл для записи выходных данных")
    parser.add_argument('--full', action='store_true', help="Использовать полное чтение данных")
    parser.add_argument('--difference', action='store_true', help="Построить автомат разности")
    parser.add_argument('--minimize', action='store_true', help="Минимизировать автомат")
    parser.add_argument('--equivalent', action='store_true', help="Проверить эквивалентность автоматов")
    parser.add_argument('--product', action='store_true', help="Построить автомат произведения двух ДКА")

    args = parser.parse_args()

    if not (args.difference or args.minimize or args.equivalent):
        print("Не указана операция для выполнения.")
        return

    # Загрузим два ДКА
    dfa1 = load_dfa(args.input_file, args.input, args.full)
    dfa2 = None
    if args.difference or args.equivalent or args.product:
        dfa2 = load_dfa(args.input_file, args.input, args.full)

    if args.difference:
        result = build_difference_automaton(dfa1, dfa2) 
    elif args.product:
        result = build_product_automaton(dfa1, dfa2)
    elif args.minimize:
        result = minimize_dfa(dfa1)
    elif args.equivalent:
        result = are_equivalent(dfa1, dfa2)
        print(f"Автоматы {'эквивалентны' if result else 'не эквивалентны'}")
        return

    write_dfa(result, args.full, args.output_file)

if __name__ == "__main__":
    main()
