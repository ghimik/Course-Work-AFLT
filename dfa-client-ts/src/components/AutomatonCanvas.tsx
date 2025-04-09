
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import rough from 'roughjs/bin/rough';
import { getArrow } from 'perfect-arrows';
import './AutomatonCanvas.css';
import { DFA } from '../types';
import { checkDifference, checkProduct, MinimezedDFA, minimizeAutomaton } from '../api';
import dagre from 'dagre';


type StateNode = {
  id: string;
  x: number;
  y: number;
  isFinal: boolean;
  isStart: boolean;
};

const mapToServerFormat = (node: StateNode) => {
  return {
    name: node.id,
    is_final: node.isFinal
  }
}

const findStartNode = (nodes: StateNode[]) => {
  const allStartNodes = nodes.filter(n => n.isStart);
  if (allStartNodes.length == 0)
    return null;
  else
    return mapToServerFormat(allStartNodes[0]);
}


type Transition = {
  source: StateNode;
  target: StateNode;
  symbol: string;
  path: string;
};


type Props = {
  height: number;
  onAutomatonUpdate: (automaton: DFA) => void;
  otherAutomaton?: DFA | null; // Получаем второй автомат через пропс

};

const AutomatonCanvas: React.FC<Props> = ({ height, onAutomatonUpdate, otherAutomaton }) => {
  const [nodes, setNodes] = useState<StateNode[]>([]);
  const [transitions, setTransitions] = useState<Transition[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [isTableView, setIsTableView] = useState(false); // для переключения между графом и таблицей

  const clickTimeoutRef = useRef<number | null>(null);

  const rc = useMemo(() => rough.svg(document.createElementNS('http://www.w3.org/2000/svg', 'svg')), []);
  const nodeSvgCache = useMemo(() => new Map<string, string>(), []);

  const [isCtrlPressed, setIsCtrlPressed] = useState(false);

  const renderTableView = () => {
    const alphabet = Array.from(new Set(transitions.map(t => t.symbol)));
    
    return (
      <table className="transition-table">
        <thead>
          <tr>
            <th>Состояние</th>
            {alphabet.map(symbol => (
              <th key={symbol}>{symbol}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {nodes.map(node => (
            <tr key={node.id}>
              {/* Проверка, является ли состояние конечным */}
              <td>
                {node.isFinal ? `*${node.id}` : node.id}
              </td>
              {alphabet.map(symbol => {
                const transition = transitions.find(
                  t => t.source.id === node.id && t.symbol === symbol
                );
                const targetState = transition ? transition.target.id : '';
                return (
                  <td key={symbol}>
                    {/* Значение в фигурных скобках */}
                    <input
                      type="text"
                      value={targetState ? `{${targetState}}` : ''}
                      onChange={e => handleTableChange(node.id, symbol, e.target.value)}
                    />
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    );
    
  };

  const handleTableChange = (nodeId: string, symbol: string, newTargetId: string) => {
    setTransitions((prevTransitions) => {
      const updatedTransitions = prevTransitions.map(t => {
        if (t.source.id === nodeId && t.symbol === symbol) {
          const newTarget = nodes.find(n => n.id === newTargetId);
          if (newTarget) {
            return { ...t, target: newTarget };
          }
        }
        return t;
      });
      return updatedTransitions;
    });
  };
  
  

  const getCurrentDFA = () => {
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
  
    const dfa: DFA = {
      states: nodes.map(mapToServerFormat),
      transitions: transitions.map(t => {
        const source = nodeMap.get(t.source.id)!;
        const target = nodeMap.get(t.target.id)!;
  
        return {
          source: mapToServerFormat(source),
          symbol: t.symbol,
          target: mapToServerFormat(target)
        };
      }),
      alphabet: Array.from(new Set(transitions.map(t => t.symbol))),
      start_state: findStartNode(nodes)
    };
    return dfa;
  }
  

  const renderNewDFA = (dfa: MinimezedDFA | null) => {
    if (!dfa) {
      setNodes([]);
      setTransitions([]);
      return;
    }
    const g = new dagre.graphlib.Graph();
    g.setGraph({});
    g.setDefaultEdgeLabel(() => ({}));
  
    const NODE_WIDTH = 40;
    const NODE_HEIGHT = 40;
  
    // Добавляем вершины
    dfa.states.forEach((state) => {
      g.setNode(state.name, { width: NODE_WIDTH, height: NODE_HEIGHT });
    });
  
    // Добавляем рёбра
    dfa.transitions.forEach((t) => {
      g.setEdge(t.source, t.target);
    });
  
    // Вычисляем layout
    dagre.layout(g);
  
    const newNodes = dfa.states.map((state) => {
      const node = g.node(state.name);
      return {
        id: state.name,
        isFinal: state.is_final,
        isStart: dfa.start_state === state.name,
        x: node.x + 40,
        y: node.y + 100
      };
    });
  
    const newTransitions = dfa.transitions
      .map((t) => {
        const sourceNode = newNodes.find(n => n.id === t.source);
        const targetNode = newNodes.find(n => n.id === t.target);
  
        if (sourceNode && targetNode) {
          let arrowPath;
          if (sourceNode.id == targetNode.id) {
            const nodeRadius = 20;
            const loopRadius = 30;
            const loopHeight = 50;
            const startX = sourceNode.x + nodeRadius;
            const startY = sourceNode.y;
            const endX = targetNode.x - nodeRadius;
            const endY = targetNode.y;
            
            arrowPath = `M ${startX} ${startY} 
                    C ${startX + loopRadius} ${startY - loopHeight/2}, 
                      ${startX + loopRadius} ${startY - loopHeight}, 
                      ${targetNode.x} ${startY - loopHeight}
                    C ${endX - loopRadius} ${startY - loopHeight}, 
                      ${endX - loopRadius} ${startY - loopHeight/2}, 
                      ${endX} ${endY}`;
          } else {
            const [sx, sy, cx, cy, ex, ey] = getArrow(
              sourceNode.x, sourceNode.y, targetNode.x, targetNode.y,
              { padStart: 20, padEnd: 20, bow: 0.1, stretch: 0.1 }
            );
            arrowPath = `M ${sx} ${sy} Q ${cx} ${cy} ${ex} ${ey}`;
          }
          return {
            symbol: t.symbol,
            source: sourceNode,
            target: targetNode,
            path: arrowPath
          }; 
        } else {
          return null;
        }
      })
      .filter((t): t is Transition => t !== null);
  
    setNodes(newNodes);
    setTransitions(newTransitions);
  }

  const handleMinimize = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    try {
      const dfa: DFA = getCurrentDFA();
  
      const minimized = await minimizeAutomaton(dfa);
      
      renderNewDFA(minimized)
      
    } catch (error) {
      console.error('Ошибка минимизации левого автомата', error);
    }
  };

  const handleDifference = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    try {
      if (!otherAutomaton) {
        console.error('Нет второго автомата для операции разности');
        return;
      }

      const dfa: DFA = getCurrentDFA();
      const difference = await checkDifference([dfa, otherAutomaton]);
      renderNewDFA(difference);
    } catch (error) {
      console.error('Ошибка выполнения операции разности', error);
    }
  };

  const handleClear = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    renderNewDFA(null);
   }

  // New handler for product operation
  const handleProduct = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    try {
      if (!otherAutomaton) {
        console.error('Нет второго автомата для операции произведения');
        return;
      }

      const dfa: DFA = getCurrentDFA();
      const product = await checkProduct([dfa, otherAutomaton]);
      renderNewDFA(product);
    } catch (error) {
      console.error('Ошибка выполнения операции произведения', error);
    }
  };
  


  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Control') {
        setIsCtrlPressed(true);
      }
    };
    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.key === 'Control') {
        setIsCtrlPressed(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  useEffect(() => {
    if (onAutomatonUpdate) {
      onAutomatonUpdate(getCurrentDFA());
    }
  }, [nodes, transitions, onAutomatonUpdate]);

  const getTextOffset = (fromY: number, toY: number) => {
    // Если переход идет вверх (от большего Y к меньшему)
    if (fromY > toY) {
      return {xOffset: 10, yOffset: 20}; // Смещаем текст выше
    } 
    // Если переход идет вниз (от меньшего Y к большему)
    else if (fromY < toY) {
      return {xOffset: 10, yOffset: -20}; // Смещаем текст ниже
    }
    // Для горизонтальных переходов
    return {xOffset: 10, yOffset: -20};
  };

  const getNodeSvg = useCallback((node: StateNode) => {
    const isSelected = selectedNode === node.id;
    const cacheKey = `${node.id}-${node.isStart}-${node.isFinal}-${isSelected}`;
    
    if (nodeSvgCache.has(cacheKey)) {
      return nodeSvgCache.get(cacheKey)!;
    }

    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("width", "50");
    svg.setAttribute("height", "50");
    svg.setAttribute("viewBox", "0 0 50 50");

    // Основной круг
    const outerCircle = rc.circle(25, 25, 35, {
      roughness: 0.8,
      stroke: isSelected ? 'red' : (node.isStart ? 'blue' : 'black'),
      fill: 'rgba(255, 255, 255, 0)',
      strokeWidth: isSelected ? 3 : 2,
      seed: parseInt(node.id.replace(/\D/g, '').slice(0, 9)) || 1
    });
    svg.appendChild(outerCircle);

    // Внутренний круг для конечного состояния
    if (node.isFinal) {
      const innerCircle = rc.circle(25, 25, 25, {
        roughness: 0.8,
        stroke: isSelected ? 'red' : (node.isStart ? 'blue' : 'black'),
        fill: 'rgba(255, 255, 255, 0)',
        strokeWidth: isSelected ? 3 : 2,
        seed: parseInt(node.id.replace(/\D/g, '').slice(0, 9)) || 1
      });
      svg.appendChild(innerCircle);
    }

    // Текст состояния
    const text = document.createElementNS(svgNS, "text");
    text.setAttribute("x", "25");
    text.setAttribute("y", "30");
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("font-size", "18");
    text.setAttribute("fill", isSelected ? "red" : "black");
    text.textContent = node.id;
    svg.appendChild(text);

    const svgString = new XMLSerializer().serializeToString(svg);
    nodeSvgCache.set(cacheKey, svgString);
    return svgString;
  }, [nodeSvgCache, rc, selectedNode]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Создаем новую ноду только по ЛКМ
    if (e.button !== 0 || isCtrlPressed || isTableView) return;
    
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const newNode: StateNode = {
      id: uuidv4().slice(0,2),
      x,
      y,
      isFinal: false,
      isStart: false,
    };

    setNodes([...nodes, newNode]);
  };

  const handleNodeRightClick = (e: React.MouseEvent, nodeId: string) => {
    e.preventDefault();
    e.stopPropagation();
    
    setNodes(nodes.map(node => {
      if (node.id === nodeId) {
        // Циклическое переключение: обычное → стартовое → конечное → обычное
        if (!node.isStart && !node.isFinal) {
          return { ...node, isStart: true, isFinal: false };
        } else if (node.isStart && !node.isFinal) {
          return { ...node, isStart: true, isFinal: true };  // Начальное и конечное
        } else if (!node.isStart && node.isFinal) {
          return { ...node, isStart: false, isFinal: false };
        } else {
          return { ...node, isStart: false, isFinal: true };
        }
      }
      return node;
    }));
  };

  const handleTransitionClick = (e: React.MouseEvent, transition: Transition) => {
    console.log("ckick fixed")
    if (isCtrlPressed) {
      setTransitions(transitions.filter(t => t !== transition));
    }
  };

  const handleNodeClick = (e: React.MouseEvent, nodeId: string) => {
    // Обрабатываем только ЛКМ
    if (e.button !== 0) return;
    e.stopPropagation();

    // Ожидаем, не будет ли double click
    if (clickTimeoutRef.current) {
      clearTimeout(clickTimeoutRef.current);
      clickTimeoutRef.current = null;
    }

    clickTimeoutRef.current = setTimeout(() => {
      if (isCtrlPressed) {
        // Удаляем состояние
        setNodes(nodes.filter(node => node.id !== nodeId));
        setTransitions(transitions.filter(t => t.source.id !== nodeId && t.target.id !== nodeId));
        return;
      }
      
      if (selectedNode === null) {
        setSelectedNode(nodeId);
      } else {
        const symbol = prompt('Введите символ перехода') || '';
        if (symbol.trim() !== '') {
          const from = nodes.find((n) => n.id === selectedNode);
          const to = nodes.find((n) => n.id === nodeId);
          if (from && to) {
            let path = '';
            if (from.id === to.id) {
              const nodeRadius = 20;
              const loopRadius = 30;
              const loopHeight = 50;
              const startX = from.x + nodeRadius;
              const startY = from.y;
              const endX = from.x - nodeRadius;
              const endY = from.y;
              
              path = `M ${startX} ${startY} 
                      C ${startX + loopRadius} ${startY - loopHeight/2}, 
                        ${startX + loopRadius} ${startY - loopHeight}, 
                        ${from.x} ${startY - loopHeight}
                      C ${endX - loopRadius} ${startY - loopHeight}, 
                        ${endX - loopRadius} ${startY - loopHeight/2}, 
                        ${endX} ${endY}`;
            } else {
              const [sx, sy, cx, cy, ex, ey] = getArrow(
                from.x, from.y, to.x, to.y,
                { padStart: 20, padEnd: 20, bow: 0.1, stretch: 0.1 }
              );
              path = `M ${sx} ${sy} Q ${cx} ${cy} ${ex} ${ey}`;
            }
            setTransitions([...transitions, { source: from, target: to, symbol, path }]);
          }
        }
        setSelectedNode(null);
      }
    }, 200)
  };

  const handleNodeDoubleClick = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();

    if (clickTimeoutRef.current) {
      clearTimeout(clickTimeoutRef.current);
      clickTimeoutRef.current = null;
    }
    const currentName = nodeId;
    const newName = prompt('Введите новое имя состояния:', currentName);
  
    if (newName && newName !== currentName) {
      // Обновляем nodes
      setNodes(prev =>
        prev.map(node =>
          node.id === nodeId ? { ...node, id: newName } : node
        )
      );
  
      // Обновляем transitions
      setTransitions(prev =>
        prev.map(t => ({
          ...t,
          source: t.source.id === nodeId ? { ...t.source, id: newName } : t.source,
          target: t.target.id === nodeId ? { ...t.target, id: newName } : t.target,
        }))
      );
    }
  };
  

  return (
    <div 
      className="notebook-bg" 
      style={{ height }} 
      onClick={handleCanvasClick}
      onContextMenu={(e) => e.preventDefault()}
    >
      <div className="buttons-container">
        <button
          className="minimize-button"
          onClick={handleMinimize}
        >
          Минимизировать автомат
        </button>

        <button className="difference-button" onClick={handleDifference}>
          Разность автомата
        </button>

        <button className="product-button" onClick={handleProduct}>
          Произведение автомата
        </button>

        <button className="clear-button" onClick={handleClear}>
          Очистить холст
        </button>
      </div>

      <div className="view-toggle">
        <label
          onClick={(e) => e.stopPropagation()}>
          <input
            type="checkbox"
            checked={isTableView}
            onChange={(e) => setIsTableView(e.target.checked)}
            onClick={(e) => e.stopPropagation()}
          />
          Табличный вид
        </label>
      </div>

      {isTableView ? renderTableView() : (
        <>
          {nodes.map((node) => (
            <div
              key={node.id}
              className={`state-node ${selectedNode === node.id ? 'selected' : ''}`}
              onClick={(e) => handleNodeClick(e, node.id)}
              onDoubleClick={(e) => handleNodeDoubleClick(e, node.id)}
              onContextMenu={(e) => handleNodeRightClick(e, node.id)}
              style={{
                left: node.x - 20,
                top: node.y - 20,
                position: 'absolute',
                width: '40px',
                height: '40px',
              }}
            >
              <div dangerouslySetInnerHTML={{ __html: getNodeSvg(node) }} />
              {node.isStart && (
                <div className="start-arrow" style={{
                  position: 'absolute',
                  left: '-15px',
                  top: '50%',
                  transform: 'translateY(-100%) translateX(25%)  rotate(45deg)',
                  fontSize: '20px',
                  color: 'blue'
                }}>→</div>
              )}
            </div>
          ))}

          <svg className="transition-layer">
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="black" />
              </marker>
            </defs>

            {Object.entries(
              transitions.reduce((acc, t) => {
                const key = `${t.source.id}_${t.target.id}`;
                if (!acc[key]) {
                  acc[key] = { ...t, symbols: [t.symbol] };
                } else {
                  acc[key].symbols.push(t.symbol);
                }
                return acc;
              }, {} as Record<string, Transition & { symbols: string[] }>)
            ).map(([key, t], i) => {
              const {xOffset, yOffset } = getTextOffset(t.source.y, t.target.y);
              const label = t.symbols.join(', ');
              return (
                <g key={i}>
                  <path
                    d={t.path}
                    stroke="black"
                    strokeWidth="2"
                    fill="none"
                    markerEnd="url(#arrowhead)"
                    onClick={(e) => handleTransitionClick(e, t)}
                    style={{ cursor: 'pointer', pointerEvents: 'all' }}
                  />
                  <text
                    x={(t.source.x + t.target.x) / 2 + xOffset}
                    y={(t.source.y + t.target.y) / 2 + yOffset}
                    fontSize="24"
                    fill="black"
                    textAnchor="middle"
                    onClick={(e) => handleTransitionClick(e, t)}
                    style={{ cursor: 'pointer', pointerEvents: 'all' }}
                  >
                    {label}
                  </text>
                </g>
              );
            })}


          </svg>
        </>
      )}


    </div>
  );
};

export default AutomatonCanvas;

