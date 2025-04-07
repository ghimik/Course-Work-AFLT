// types.ts
export interface State {
    name: string;
    is_final: boolean;
  }
  
  export interface Transition {
    from: string;
    symbol: string;
    to: string;
  }
  
  export interface DFA {
    states: State[];
    transitions: Transition[];
    alphabet: string[];
    start_state: string;
  }
  
  export interface EquivalenceResponse {
    equivalent: boolean;
  }

