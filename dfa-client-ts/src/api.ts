// api.ts
import { DFA, EquivalenceResponse } from './types';

const API_BASE_URL = 'http://localhost:5000'; // Замените на ваш бекенд URL

// Интерфейс состояния
interface MinimezedState {
    name: string;  // Название состояния
    is_final: boolean;  // Является ли состояние финальным
  }
  
  // Интерфейс перехода
  interface MinimezedTransition {
    source: string;  // Идентификатор исходного состояния
    symbol: string;  // Символ на который происходит переход
    target: string;  // Идентификатор целевого состояния
  }
  
  // Интерфейс минимизированного автомата
  export interface MinimezedDFA {
    states: MinimezedState[];  // Массив состояний
    transitions: MinimezedTransition[];  // Массив переходов
    alphabet: string[];  // Алфавит (массив символов)
    start_state: string | null;  // Начальное состояние (строка или null)
  }
  



export const minimizeAutomaton = async (automaton: DFA): Promise<MinimezedDFA> => {
  try {
    const response = await fetch(`${API_BASE_URL}/minimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(automaton),  // Отправляем один автомат
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;  // Предполагаем, что сервер вернет один минимизированный автомат
  } catch (error) {
    console.error('Error minimizing automaton:', error);
    throw error;
  }
};


export const checkEquivalence = async (automata: DFA[]): Promise<EquivalenceResponse> => {
  try {
    console.log("sent automata: "+ JSON.stringify(automata));
    const response = await fetch(`${API_BASE_URL}/equivalence`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(automata),
    });


    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return await result as EquivalenceResponse;
  } catch (error) {
    console.error('Error checking equivalence:', error);
    throw error;
  }
};

// Пример использования (для тестов)
export const mockCheckEquivalence = async (automata: DFA[]): Promise<EquivalenceResponse> => {
  console.log('Mock equivalence check for:', automata);
  await new Promise(resolve => setTimeout(resolve, 5)); // Имитация задержки сети
  return { equivalent: Math.random() < 0.5 }; // Всегда возвращает true в моке
};

export const checkDifference = async (automata: DFA[]): Promise<MinimezedDFA> => {
    if (automata.length !== 2) {
        throw new Error("Необходимо передать два автомата для вычисления различия");
    }
    try {
        const response = await fetch(`${API_BASE_URL}/difference`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(automata),
        });

        if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return result;  // Возвращаем результат различия
    } catch (error) {
        console.error('Error checking difference:', error);
        throw error;
    }
};

// Новый эндпоинт для произведения автоматов
export const checkProduct = async (automata: DFA[]): Promise<MinimezedDFA> => {
    if (automata.length !== 2) {
        throw new Error("Необходимо передать два автомата для вычисления произведения");
    }
    try {
        const response = await fetch(`${API_BASE_URL}/product`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(automata),
        });

        if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return result;  // Возвращаем результат произведения
    } catch (error) {
        console.error('Error checking product:', error);
        throw error;
    }
};