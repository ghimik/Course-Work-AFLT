
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import rough from 'roughjs/bin/rough';
import { getArrow } from 'perfect-arrows';
import './AutomatonCanvas.css';
import { DFA } from '../types';

type StateNode = {
  id: string;
  x: number;
  y: number;
  isFinal: boolean;
  isStart: boolean;
};

type Transition = {
  from: StateNode;
  to: StateNode;
  symbol: string;
  path: string;
};

type Props = {
  height: number;
  onAutomatonUpdate: (automaton: DFA) => void
};

const AutomatonCanvas: React.FC<Props> = ({ height, onAutomatonUpdate }) => {
  const [nodes, setNodes] = useState<StateNode[]>([]);
  const [transitions, setTransitions] = useState<Transition[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  
  const rc = useMemo(() => rough.svg(document.createElementNS('http://www.w3.org/2000/svg', 'svg')), []);
  const nodeSvgCache = useMemo(() => new Map<string, string>(), []);

  useEffect(() => {
    if (onAutomatonUpdate) {
      const dfa: DFA = {
        states: nodes.map(node => ({
          name: node.id,
          is_final: node.isFinal
        })),
        transitions: transitions.map(t => ({
          from: t.from.id,
          symbol: t.symbol,
          to: t.to.id
        })),
        alphabet: Array.from(new Set(transitions.map(t => t.symbol))),
        start_state: nodes.find(n => n.isStart)?.id || ''
      };
      onAutomatonUpdate(dfa);
    }
  }, [nodes, transitions, onAutomatonUpdate]);

  const getTextOffset = (fromY: number, toY: number) => {
    // Если переход идет вверх (от большего Y к меньшему)
    if (fromY > toY) {
      return 20; // Смещаем текст выше
    } 
    // Если переход идет вниз (от меньшего Y к большему)
    else if (fromY < toY) {
      return -20; // Смещаем текст ниже
    }
    // Для горизонтальных переходов
    return 0;
  };

  const getNodeSvg = useCallback((node: StateNode) => {
    const isSelected = selectedNode === node.id;
    const cacheKey = `${node.id}-${node.isStart}-${node.isFinal}-${isSelected}`;
    
    if (nodeSvgCache.has(cacheKey)) {
      return nodeSvgCache.get(cacheKey)!;
    }

    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("width", "80");
    svg.setAttribute("height", "80");
    svg.setAttribute("viewBox", "0 0 80 80");

    // Основной круг
    const outerCircle = rc.circle(40, 40, 35, {
      roughness: 0.8,
      stroke: isSelected ? 'red' : (node.isStart ? 'blue' : 'black'),
      fill: 'rgba(255, 255, 255, 0)',
      strokeWidth: isSelected ? 3 : 2,
      seed: parseInt(node.id.replace(/\D/g, '').slice(0, 9)) || 1
    });
    svg.appendChild(outerCircle);

    // Внутренний круг для конечного состояния
    if (node.isFinal) {
      const innerCircle = rc.circle(40, 40, 25, {
        roughness: 0.8,
        stroke: isSelected ? 'red' : 'black',
        fill: 'rgba(255, 255, 255, 0)',
        strokeWidth: isSelected ? 3 : 2,
        seed: parseInt(node.id.replace(/\D/g, '').slice(0, 9)) || 1
      });
      svg.appendChild(innerCircle);
    }

    // Текст состояния
    const text = document.createElementNS(svgNS, "text");
    text.setAttribute("x", "40");
    text.setAttribute("y", "45");
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("font-size", "18");
    text.setAttribute("fill", isSelected ? "red" : "black");
    text.textContent = node.id.slice(0, 2).toUpperCase();
    svg.appendChild(text);

    const svgString = new XMLSerializer().serializeToString(svg);
    nodeSvgCache.set(cacheKey, svgString);
    return svgString;
  }, [nodeSvgCache, rc, selectedNode]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Создаем новую ноду только по ЛКМ
    if (e.button !== 0) return;
    
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const newNode: StateNode = {
      id: uuidv4(),
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
        } else if (node.isStart) {
          return { ...node, isStart: false, isFinal: true };
        } else {
          return { ...node, isStart: false, isFinal: false };
        }
      }
      return node;
    }));
  };

  const handleNodeClick = (e: React.MouseEvent, nodeId: string) => {
    // Обрабатываем только ЛКМ
    if (e.button !== 0) return;
    e.stopPropagation();
    
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
          setTransitions([...transitions, { from, to, symbol, path }]);
        }
      }
      setSelectedNode(null);
    }
  };

  return (
    <div 
      className="notebook-bg" 
      style={{ height }} 
      onClick={handleCanvasClick}
      onContextMenu={(e) => e.preventDefault()}
    >
      {nodes.map((node) => (
        <div
          key={node.id}
          className={`state-node ${selectedNode === node.id ? 'selected' : ''}`}
          onClick={(e) => handleNodeClick(e, node.id)}
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

        {transitions.map((t, i) => {
          const yOffset = getTextOffset(t.from.y, t.to.y);
          return (
            <g key={i}>
              <path
                d={t.path}
                stroke="black"
                strokeWidth="2"
                fill="none"
                markerEnd="url(#arrowhead)"
              />
              <text
                x={(t.from.x + t.to.x) / 2}
                y={(t.from.y + t.to.y) / 2 + yOffset}
                fontSize="24"
                fill="black"
                textAnchor="middle"
              >
                {t.symbol}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

export default AutomatonCanvas;