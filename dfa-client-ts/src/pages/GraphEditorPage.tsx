// GraphEditorPage.tsx
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import AutomatonCanvas from '../components/AutomatonCanvas';
import { checkEquivalence, mockCheckEquivalence } from '../api';
import '../styles/notebook.css';
import { DFA } from '../types';

const GraphEditorPage: React.FC = () => {
  const [leftAutomaton, setLeftAutomaton] = useState<DFA | null>(null);
  const [rightAutomaton, setRightAutomaton] = useState<DFA | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [equivalenceResult, setEquivalenceResult] = useState<boolean | null>(null);
  const [message, setMessage] = useState<string|null>(null);

  const { pageHeight, pageWidth } = useMemo(() => {
    const maxHeight = Math.min(window.innerHeight * 0.85, 900);
    const ratio = 1.414;
    return {
      pageHeight: maxHeight,
      pageWidth: maxHeight * ratio
    };
  }, []);



  const canvasHeight = pageHeight - 40;

  const handleCheckEquivalence = async () => {
    if (!leftAutomaton || !rightAutomaton) {
      setMessage('Оба автомата должны быть определены, двойка!');
      return;
    }

    setIsChecking(true);
    setEquivalenceResult(null);
    
    try {
      // Используйте mockCheckEquivalence для тестов без бекенда
      // или checkEquivalence для реальных запросов
      const result = await mockCheckEquivalence([leftAutomaton, rightAutomaton]);
      setEquivalenceResult(result.equivalent);
      setMessage(result.equivalent? 'Эквивалентны, Кириллов!': 'Не эквивалентны, Кириллов!');
      
    } catch (error) {
      console.error('Error:', error);
      setMessage('Учитель спит, не получилось проверить');
    } finally {
      setIsChecking(false);
    }
  };


  // Функции для обновления автоматов (должны вызываться из AutomatonCanvas)
  const updateLeftAutomaton = useCallback((automaton: DFA) => {
    setLeftAutomaton(automaton);
  }, []);
  
  const updateRightAutomaton = useCallback((automaton: DFA) => {
    setRightAutomaton(automaton);
  }, []);

  useEffect(() => {
    const canvas = document.getElementById('starfield-canvas') as HTMLCanvasElement;
    if (!canvas) return;
  
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
  
    let width = window.innerWidth;
    let height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.zIndex = '0';
  
    const numStars = 300;
    const stars = Array.from({ length: numStars }, () => ({
      x: Math.random() * width - width / 2,
      y: Math.random() * height - height / 2,
      z: Math.random() * width,
    }));
  
    const animate = () => {
      ctx.fillStyle = 'black';
      ctx.fillRect(0, 0, width, height);
  
      for (let star of stars) {
        star.z -= 2;
        if (star.z <= 0) star.z = width;
  
        const k = 128.0 / star.z;
        const x = star.x * k + width / 2;
        const y = star.y * k + height / 2;
  
        if (x < 0 || x >= width || y < 0 || y >= height) continue;
  
        const size = (1 - star.z / width) * 3;
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(x, y, size, 0, 2 * Math.PI);
        ctx.fill();
      }
  
      requestAnimationFrame(animate);
    };
  
    animate();
  
    const handleResize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
    };
  
    window.addEventListener('resize', handleResize);
  
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  

  return (
    <div className="desk-container">
      <canvas id="starfield-canvas" />
      <div className="notebook-page" style={{ 
        width: `${pageWidth}px`,
        height: `${pageHeight}px`,
        maxWidth: '95vw'
      }}>
        <div className="page-left">
          <AutomatonCanvas 
            height={canvasHeight} 
            onAutomatonUpdate={updateLeftAutomaton}
          />
        </div>
        <div className="page-right">
          <AutomatonCanvas 
            height={canvasHeight} 
            onAutomatonUpdate={updateRightAutomaton}
          />
          {/* Добавляем результат прямо на страницу тетради */}
          {equivalenceResult !== null && (
            <div className={`handwritten-result ${equivalenceResult ? 'equivalent' : 'not-equivalent'}`}>
              {message}
            </div>
          )}
        </div>
      </div>
      
      <button 
        className="equivalence-button"
        onClick={handleCheckEquivalence}
        disabled={isChecking}
      >
        {isChecking ? 'Проверяем...' : 'Проверить на эквивалентность'}
      </button>
    </div>
  );
};

export default GraphEditorPage;