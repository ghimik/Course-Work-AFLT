// api.ts
import { DFA, EquivalenceResponse } from './types';

const API_BASE_URL = 'http://localhost:5000'; // Замените на ваш бекенд URL

export const checkEquivalence = async (automata: DFA[]): Promise<EquivalenceResponse> => {
  try {
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

    return await response.json() as EquivalenceResponse;
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