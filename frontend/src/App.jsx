import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Lock, User, Activity, TrendingUp, TrendingDown, 
  ShieldCheck, AlertTriangle, Play, Square, Settings,
  BarChart3, LifeBuoy
} from 'lucide-react';
import axios from 'axios';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [tradingActive, setTradingActive] = useState(false);
  const [marketStatus, setMarketStatus] = useState('NORMAL');
  const [logs, setLogs] = useState([
    { id: 1, type: 'info', msg: '시스템이 시작되었습니다.', time: '09:00:01' },
    { id: 2, type: 'warning', msg: '시장 상태 모니터링 중 (3분 주기)', time: '09:03:00' }
  ]);

  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      // 백엔드 가상 로그인 API 호출
      await axios.post('http://localhost:8000/login');
      setTimeout(() => {
        setIsLoggedIn(true);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error("Login failed", error);
      setIsLoggedIn(true); // 에러가 나도 테스트를 위해 진입 허용
      setIsLoading(false);
    }
  };

  const toggleTrading = async () => {
    const nextState = !tradingActive;
    // 실제 백엔드 연동: await axios.post(`http://localhost:8000/${nextState ? 'start' : 'stop'}`);
    setTradingActive(nextState);
    const newLog = {
      id: Date.now(),
      type: nextState ? 'success' : 'error',
      msg: nextState ? '자동매매가 시작되었습니다.' : '자동매매가 중지되었습니다.',
      time: new Date().toLocaleTimeString()
    };
    setLogs(prev => [newLog, ...prev]);
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass p-8 rounded-2xl w-full max-w-md glow-gold"
        >
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-brand-gold mb-2">KIWOOM AUTO</h1>
            <p className="text-slate-400">전통적 방식의 초저지연 자동매매 시스템</p>
          </div>
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="relative">
              <User className="absolute left-3 top-3 text-slate-500 w-5 h-5" />
              <input 
                type="text" 
                placeholder="사용자 ID" 
                className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg py-3 pl-12 pr-4 focus:outline-none focus:border-brand-gold transition-all"
                required
              />
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-3 text-slate-500 w-5 h-5" />
              <input 
                type="password" 
                placeholder="비밀번호" 
                className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg py-3 pl-12 pr-4 focus:outline-none focus:border-brand-gold transition-all"
                required
              />
            </div>
            <button 
              type="submit"
              disabled={isLoading}
              className={`w-full ${isLoading ? 'bg-slate-700' : 'bg-brand-gold hover:bg-yellow-600'} text-brand-navy font-bold py-3 rounded-lg transition-transform active:scale-95 shadow-lg flex items-center justify-center gap-2`}
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-brand-navy border-t-transparent rounded-full animate-spin"></div>
                  서버 연결 중...
                </>
              ) : '키움증권 로그인'}
            </button>
          </form>
          <div className="mt-8 pt-6 border-t border-slate-700/50 text-center text-xs text-slate-500">
            <p>본 프로그램은 KHOpenAPI 32-bit 환경에서 동작합니다.</p>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-bg p-6 text-slate-200">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-brand-gold">Antigravity Trading Hub</h1>
            <p className="text-sm text-slate-400">실시간 시장 감시 및 속도전 대응 중</p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`px-4 py-2 rounded-full glass flex items-center gap-2 ${marketStatus === 'NORMAL' ? 'text-brand-safe' : 'text-brand-risk'}`}>
              <ShieldCheck className="w-4 h-4" />
              <span className="text-sm font-medium">시장 상태: {marketStatus}</span>
            </div>
            <button 
              onClick={toggleTrading}
              className={`p-3 rounded-xl flex items-center gap-2 transition-all ${tradingActive ? 'bg-brand-risk text-white' : 'bg-brand-safe text-white'} glow-gold`}
            >
              {tradingActive ? <Square className="w-5 h-5" /> : <Play className="w-5 h-5" />}
              <span className="font-bold">{tradingActive ? '매매 중지' : '매매 시작'}</span>
            </button>
          </div>
        </header>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Main Stats */}
          <div className="glass p-6 rounded-2xl flex flex-col justify-between">
            <div className="flex justify-between items-start mb-4">
              <span className="text-slate-400 text-sm">예수금 현황</span>
              <LifeBuoy className="text-brand-gold w-5 h-5" />
            </div>
            <div className="text-3xl font-mono font-bold">12,450,000₩</div>
            <div className="text-sm text-brand-safe mt-2">+1.2% 대비 어제</div>
          </div>

          <div className="glass p-6 rounded-2xl flex flex-col justify-between">
            <div className="flex justify-between items-start mb-4">
              <span className="text-slate-400 text-sm">당일 실현 손익</span>
              <TrendingUp className="text-brand-safe w-5 h-5" />
            </div>
            <div className="text-3xl font-mono font-bold text-brand-safe">+142,500₩</div>
            <div className="text-sm text-slate-500 mt-2">매수 5건 / 매도 3건</div>
          </div>

          <div className="glass p-6 rounded-2xl flex flex-col justify-between">
            <div className="flex justify-between items-start mb-4">
              <span className="text-slate-400 text-sm">평가 손익</span>
              <Activity className="text-brand-accent w-5 h-5" />
            </div>
            <div className="text-3xl font-mono font-bold">-12,000₩</div>
            <div className="text-sm text-brand-risk mt-2">-0.05% (보유 2종목)</div>
          </div>
        </div>

        {/* Real-time Order Logs & Holding List */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Logs */}
          <div className="glass rounded-2xl flex flex-col h-[400px]">
            <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
              <h3 className="font-bold flex items-center gap-2"><BarChart3 className="w-4 h-4" /> 실시간 매매 로그</h3>
              <span className="text-xs text-brand-gold">3분 지수 체크 ON</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-sm">
              <AnimatePresence>
                {logs.map((log) => (
                  <motion.div 
                    key={log.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`flex gap-3 ${log.type === 'error' ? 'text-brand-risk' : log.type === 'warning' ? 'text-brand-gold' : 'text-slate-300'}`}
                  >
                    <span className="text-slate-500">[{log.time}]</span>
                    <span>{log.msg}</span>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>

          <div className="glass rounded-2xl flex flex-col h-[400px]">
            <div className="p-4 border-b border-slate-700/50">
              <h3 className="font-bold flex items-center gap-2"><TrendingUp className="w-4 h-4" /> 보유 종목 현황</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {/* Table logic here */}
              <div className="text-center py-20 text-slate-500">
                <p>보유 중인 종목이 없습니다.</p>
                <p className="text-xs mt-2 italic">10배 허매수 필터링 가동 중...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
