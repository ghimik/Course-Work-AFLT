// types.ts
export interface State {
    name: string;
    is_final: boolean;
  }
  
  export interface Transition {
    source: State;
    symbol: string;
    target: State;
  }
  
  export interface DFA {
    states: State[];
    transitions: Transition[];
    alphabet: string[];
    start_state: State | null;
  }
  
  export interface EquivalenceResponse {
    equivalent: boolean;
  }

