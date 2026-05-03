import { useState, useCallback, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [scoutData, setScoutData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [managerIdInput, setManagerIdInput] = useState('');
  const [viewMode, setViewMode] = useState('optimized'); // 'optimized' or 'current'

  const fetchData = useCallback(async (targetId = null) => {
    setLoading(true);
    setError(null);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const url = targetId 
        ? `${apiUrl}/api/scout-report?manager_id=${targetId}` 
        : `${apiUrl}/api/scout-report`;
        
      const scoutResponse = await fetch(url);
      
      if (!scoutResponse.ok) {
        const errorData = await scoutResponse.json();
        throw new Error(errorData.detail || 'Failed to fetch data from backend');
      }
      
      const scout = await scoutResponse.json();
      setScoutData(scout);
      setViewMode('optimized'); // reset view mode on fresh fetch
    } catch (err) {
      setError(err.message);
      setScoutData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (managerIdInput.trim()) {
      fetchData(managerIdInput.trim());
    }
  };

  const loadAdminTeam = () => {
    fetchData(null);
  };

  // If no data and not loading, show the Landing Screen
  if (!scoutData && !loading) {
    return (
      <div className="min-h-screen bg-[#0A0D14] flex flex-col items-center justify-center text-slate-300 font-mono p-4 selection:bg-emerald-500/30">
        <div className="max-w-md w-full space-y-8 animate-fade-in-up">
          <div className="text-center border-b border-slate-800 pb-8">
            <h1 className="text-4xl font-bold text-white tracking-tight mb-2">FPL AI <span className="text-emerald-500">Agent</span></h1>
            <p className="text-slate-500 text-sm">ADVANCED ANALYTICS & STRATEGY PROTOCOL</p>
          </div>

          {error && (
            <div className="border-l-2 border-red-500 bg-red-500/10 p-4">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <div className="bg-[#0E121C] border border-slate-800 p-6 space-y-6">
            <div>
              <label className="block text-xs text-slate-500 uppercase tracking-widest mb-3">Initialize Protocol</label>
              <form onSubmit={handleSearch} className="space-y-3">
                <input 
                  type="text" 
                  placeholder="Enter FPL Manager ID..."
                  value={managerIdInput}
                  onChange={(e) => setManagerIdInput(e.target.value)}
                  className="w-full bg-[#0A0D14] border border-slate-700 text-slate-200 text-sm px-4 py-3 focus:outline-none focus:border-emerald-500 transition-colors"
                  required
                />
                <button 
                  type="submit"
                  className="w-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/50 hover:bg-emerald-500/20 px-4 py-3 text-sm font-bold uppercase tracking-widest transition-colors"
                >
                  Analyze Squad
                </button>
              </form>
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-800"></div>
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-[#0E121C] px-2 text-slate-600 uppercase tracking-widest">Or</span>
              </div>
            </div>

            <button 
              onClick={loadAdminTeam}
              className="w-full bg-transparent text-slate-400 border border-slate-700 hover:border-slate-500 hover:text-slate-300 px-4 py-3 text-sm font-bold uppercase tracking-widest transition-colors"
            >
              View Admin Demo
            </button>
          </div>
        </div>
      </div>
    );
  }

  const activeLineup = scoutData ? (viewMode === 'optimized' ? scoutData.optimal_lineup : (scoutData.current_lineup || [])) : [];

  // Once data is loading or loaded, show the main dashboard
  return (
    <div className="min-h-screen bg-[#0A0D14] text-slate-300 font-mono p-4 md:p-8 selection:bg-emerald-500/30">
      <div className="max-w-7xl mx-auto space-y-8 pb-20">
        <header className="border-b border-slate-800 pb-6 mb-8 flex flex-col lg:flex-row justify-between items-end gap-6">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight cursor-pointer" onClick={() => setScoutData(null)}>
              FPL AI Agent
            </h1>
            <p className="text-slate-500 text-sm mt-1 mb-4">ADVANCED ANALYTICS & STRATEGY PROTOCOL</p>
            
            <form onSubmit={handleSearch} className="flex gap-2">
              <input 
                type="text" 
                placeholder="Enter FPL Manager ID..."
                value={managerIdInput}
                onChange={(e) => setManagerIdInput(e.target.value)}
                className="bg-[#0E121C] border border-slate-700 text-slate-200 text-sm px-3 py-1.5 focus:outline-none focus:border-emerald-500 w-64 transition-colors"
              />
              <button 
                type="submit"
                disabled={loading}
                className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/50 hover:bg-emerald-500/20 px-4 py-1.5 text-sm font-bold uppercase tracking-widest disabled:opacity-50 transition-colors"
              >
                Analyze
              </button>
            </form>
          </div>
          
          {scoutData && (
            <div className="flex flex-wrap gap-6">
               <div>
                  <p className="text-[10px] text-slate-500 uppercase tracking-widest">Bank Balance</p>
                  <p className="text-xl text-emerald-400 font-bold">£{scoutData.bank.toFixed(1)}m</p>
               </div>
               <div>
                  <p className="text-[10px] text-slate-500 uppercase tracking-widest">Available Chips</p>
                  <div className="flex gap-2 mt-1">
                     {scoutData.available_chips.map(c => (
                        <span key={c} className="px-2 py-0.5 border border-slate-700 text-xs text-slate-400 bg-slate-800/50">{c}</span>
                     ))}
                  </div>
               </div>
            </div>
          )}
        </header>

        {loading && (
          <div className="flex justify-center items-center h-64">
            <p className="text-emerald-500 animate-pulse">INITIATING DATA FETCH AND SQUAD ANALYSIS...</p>
          </div>
        )}

        {error && !loading && (
          <div className="border-l-2 border-red-500 bg-red-500/10 p-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {scoutData && !loading && (
          <div className="space-y-8 animate-fade-in-up">
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
              
              {/* Team Layout (Left) */}
              <div className="xl:col-span-2 space-y-6">
                <div className="flex justify-between items-center border border-slate-800 bg-[#0E121C] p-4">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase tracking-widest block">Targeting GW</span>
                    <span className="text-lg font-bold text-white">{scoutData.target_gw}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-500 uppercase tracking-widest block">Manager ID</span>
                    <span className="text-lg font-bold text-slate-300">{scoutData.manager_id}</span>
                  </div>
                </div>

                {/* View Toggle */}
                <div className="flex justify-center mb-2">
                   <div className="inline-flex bg-[#0E121C] border border-slate-800 p-1">
                      <button 
                         onClick={() => setViewMode('current')}
                         className={`px-6 py-2 text-xs font-bold uppercase tracking-widest transition-colors ${viewMode === 'current' ? 'bg-slate-800 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                      >
                         Current Lineup
                      </button>
                      <button 
                         onClick={() => setViewMode('optimized')}
                         className={`px-6 py-2 text-xs font-bold uppercase tracking-widest transition-colors ${viewMode === 'optimized' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-500 hover:text-slate-300'}`}
                      >
                         Optimized Lineup
                      </button>
                   </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border border-slate-800 bg-[#0E121C] p-4">
                    <div className="flex justify-between items-end mb-4 border-b border-slate-800 pb-2">
                      <h2 className="text-xs text-slate-500 uppercase tracking-widest">{viewMode === 'optimized' ? 'Optimized Starting XI' : 'Current Starting XI'}</h2>
                      {viewMode === 'optimized' && <span className="text-[10px] text-emerald-500 font-bold tracking-widest bg-emerald-500/10 px-2 py-0.5 border border-emerald-500/20">AUTO-CAPTAIN ENABLED</span>}
                    </div>
                    <div className="space-y-1">
                      {activeLineup.filter(p => p.status === 'Starting').map((player, idx) => {
                        const trendReason = (scoutData.trending_players || []).find(t => t.id === player.id)?.reason;
                        return <PlayerRow key={idx} player={player} trendingReason={trendReason} />;
                      })}
                    </div>
                  </div>

                  <div className="border border-slate-800 bg-[#0E121C] p-4 h-fit">
                    <div className="flex justify-between items-end mb-4 border-b border-slate-800 pb-2">
                      <h2 className="text-xs text-slate-500 uppercase tracking-widest">{viewMode === 'optimized' ? 'Optimized Bench' : 'Current Bench'}</h2>
                      {viewMode === 'optimized' && <span className="text-[10px] text-slate-500 font-bold tracking-widest">ORDERED BY EP</span>}
                    </div>
                    <div className="space-y-1">
                      {activeLineup.filter(p => p.status === 'Bench').map((player, idx) => {
                        const trendReason = (scoutData.trending_players || []).find(t => t.id === player.id)?.reason;
                        return <PlayerRow key={idx} player={player} isBench benchOrder={idx + 1} trendingReason={trendReason} />;
                      })}
                    </div>
                  </div>
                </div>
              </div>

              {/* Strategy Sidebar (Right) */}
              <div className="xl:col-span-1 space-y-4">
                <div className="border border-indigo-900/50 bg-[#0E121C] p-4">
                  <h2 className="text-xs text-indigo-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse"></div>
                    Chip Strategy
                  </h2>
                  <p className="text-sm text-slate-300 leading-relaxed">{scoutData.chip_strategy}</p>
                </div>

                <h2 className="text-xs text-emerald-500 uppercase tracking-widest pt-4 pb-2 border-b border-slate-800">Action Plans</h2>
                
                <div className="space-y-4">
                  {scoutData.action_plans.map((plan, idx) => (
                    <ActionPlanCard key={idx} plan={plan} idx={idx} trendingPlayers={scoutData.trending_players || []} playerMap={scoutData.optimal_lineup.concat(scoutData.current_lineup)} />
                  ))}
                  {scoutData.action_plans.length === 0 && (
                     <p className="text-sm text-slate-500 italic">No favorable transfers found.</p>
                  )}
                </div>
              </div>

            </div>

            {/* League Intel Bottom Hub */}
            <LeagueIntel intel={scoutData.league_intel} />

            {/* Trending Players Hub */}
            <TrendingHub trendingPlayers={scoutData.trending_players || []} />

            {/* Season Timeline Matrix */}
            <SeasonTimeline timeline={scoutData.season_timeline} targetGw={scoutData.target_gw} />

          </div>
        )}
      </div>

      {/* AI Chatbot Widget */}
      {scoutData && <AIChatWidget scoutData={scoutData} />}
      
    </div>
  );
}

function AIChatWidget({ scoutData }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "I've analyzed your squad using the official FPL Expected Points algorithm. Ask me any transfer or strategy questions!" }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping, isOpen]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsTyping(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          scout_data: scoutData,
          history: messages
        })
      });

      if (!response.ok) throw new Error('Chat API failed');
      const data = await response.json();
      
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err.message}. Ensure GROQ_API_KEY is set in backend.` }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-4">
      {isOpen && (
        <div className="w-80 sm:w-96 h-[500px] bg-[#0E121C] border border-emerald-500/30 flex flex-col shadow-2xl shadow-emerald-900/20 animate-fade-in-up">
          <div className="bg-emerald-900/20 border-b border-emerald-500/30 px-4 py-3 flex justify-between items-center">
            <h3 className="text-sm font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-2">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
              FPL AI Assistant
            </h3>
            <button onClick={() => setIsOpen(false)} className="text-slate-500 hover:text-slate-300">✕</button>
          </div>
          
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] px-3 py-2 text-sm ${
                  msg.role === 'user' 
                  ? 'bg-slate-800 text-white rounded-l-md rounded-tr-md' 
                  : 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-100 rounded-r-md rounded-tl-md'
                }`}>
                  {/* Basic markdown bold support for player names */}
                  {msg.content.split('**').map((text, i) => (
                    i % 2 === 1 ? <strong key={i} className="text-emerald-400">{text}</strong> : text
                  ))}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-emerald-500/10 border border-emerald-500/20 px-3 py-2 text-sm rounded-r-md rounded-tl-md text-emerald-400/70 animate-pulse">
                  Analyzing squad data...
                </div>
              </div>
            )}
          </div>

          <form onSubmit={sendMessage} className="border-t border-slate-800 p-3 bg-slate-900/50 flex gap-2">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask for transfer advice..."
              className="flex-1 bg-[#0A0D14] border border-slate-700 text-slate-200 text-sm px-3 py-2 focus:outline-none focus:border-emerald-500 transition-colors"
            />
            <button 
              type="submit" 
              disabled={isTyping}
              className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 hover:bg-emerald-500/30 transition-colors disabled:opacity-50"
            >
              ➤
            </button>
          </form>
        </div>
      )}
      
      {!isOpen && (
        <button 
          onClick={() => setIsOpen(true)}
          className="bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-bold w-14 h-14 rounded-full flex items-center justify-center shadow-lg shadow-emerald-500/20 transition-transform hover:scale-105"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
        </button>
      )}
    </div>
  );
}

function PlayerRow({ player, isBench, benchOrder, trendingReason }) {
  return (
    <div className={`flex justify-between items-center py-2 px-3 border-l-2 ${isBench ? 'border-slate-700 bg-slate-900/30' : 'border-emerald-500/50 hover:bg-slate-800/50'} transition-colors`}>
      <div className="flex items-center gap-3">
        {isBench && <span className="text-[9px] text-slate-600 font-bold w-3">{benchOrder === 1 ? 'GK' : `B${benchOrder - 1}`}</span>}
        <div className="flex flex-col">
          <span className={`font-semibold text-sm flex items-center gap-2 ${isBench ? 'text-slate-500' : 'text-slate-200'}`}>
            {player.name}
            {player.role_display && (
              <span className={`text-[9px] font-bold px-1.5 py-0.5 border ${
                player.role_display === '(C)' 
                ? 'border-amber-500 text-amber-400 bg-amber-500/10' 
                : 'border-slate-500 text-slate-400 bg-slate-500/10'
              }`}>
                {player.role_display === '(C)' ? 'CAP' : 'VC'}
              </span>
            )}
            {trendingReason && (
              <span className="text-[10px] cursor-help" title={`Trending on Reddit: ${trendingReason}`}>🔥</span>
            )}
          </span>
          <div className="flex items-center gap-2 mt-0.5">
             <span className="text-[9px] text-slate-500 tracking-wider font-mono">{player.fixture_display}</span>
             {player.injury_warning && (
               <span className="text-[9px] text-red-400" title={player.injury_warning}>
                 ⚠️ {player.injury_warning}
               </span>
             )}
          </div>
        </div>
      </div>
      <div className="text-right flex flex-col items-end gap-1">
        <span className="text-sm font-bold text-emerald-400 flex items-center gap-2">
          {player.is_ep_anomaly && (
            <span className="text-sm cursor-help" title="⚠️ FPL Math Anomaly: Player is fit but officially projected 0.0 points">❓</span>
          )}
          {player.ep_next.toFixed(1)}
        </span>
        {player.social_ep > player.ep_next ? (
          <span className="text-[9px] text-amber-500 font-bold bg-amber-500/10 px-1 border border-amber-500/30">
            [HYPE BOOST +{(player.social_ep - player.ep_next).toFixed(1)}]
          </span>
        ) : (
          <span className="text-[10px] text-slate-500 font-mono">£{(player.now_cost / 10).toFixed(1)}m</span>
        )}
      </div>
    </div>
  );
}

function ActionPlanCard({ plan, idx, trendingPlayers }) {
  return (
    <div className="border border-slate-800 bg-[#0E121C] group hover:border-slate-600 transition-colors">
      <div className="bg-slate-900 px-4 py-2 flex justify-between items-center border-b border-slate-800">
        <span className="text-[10px] uppercase tracking-widest text-emerald-400 font-bold">Plan 0{idx + 1}</span>
        <span className="text-[10px] text-slate-500 border border-slate-700 px-1">{plan.type}</span>
      </div>
      
      <div className="p-4 space-y-4">
        <p className="text-sm text-slate-400 leading-relaxed">{plan.explanation}</p>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <span className="text-[10px] text-red-400 uppercase tracking-widest">Sell</span>
            <div className="space-y-1">
              {plan.sell.map(p => (
                <div key={p} className="text-sm text-slate-300 border-l border-red-500/50 pl-2 py-0.5">{p}</div>
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <span className="text-[10px] text-emerald-400 uppercase tracking-widest">Buy</span>
            <div className="space-y-1">
              {plan.buy.map(p => {
                const isTrending = trendingPlayers.find(t => t.name === p);
                return (
                  <div key={p} className="text-sm text-white font-semibold border-l border-emerald-500/50 pl-2 py-0.5 flex flex-col gap-0.5">
                    <div className="flex items-center gap-1">
                      {p}
                      {isTrending && <span className="text-[10px] cursor-help" title={`Trending on Reddit: ${isTrending.reason}`}>🔥</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        
        <div className="flex justify-between items-center pt-3 border-t border-slate-800/50">
           <span className="text-[10px] text-slate-500 uppercase">Est. EP Gain</span>
           <span className="text-sm font-bold text-emerald-400">+{plan.net_ep_gain}</span>
        </div>
      </div>
    </div>
  );
}

function LeagueIntel({ intel }) {
  if (!intel) return null;

  return (
    <div className="mt-12">
      <h2 className="text-xl font-bold text-white tracking-tight mb-4 flex items-center gap-3">
         <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
         League Intel Terminal
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Injury Ward */}
        <div className="border border-slate-800 bg-[#0E121C] p-4 lg:col-span-2 h-64 overflow-y-auto custom-scrollbar">
          <h3 className="text-[10px] text-red-400 uppercase tracking-widest border-b border-slate-800 pb-2 mb-3 sticky top-0 bg-[#0E121C] z-10">Injury Ward (Top Owned)</h3>
          <div className="space-y-2">
            {intel.injury_ward.map((p, i) => (
              <div key={i} className="flex justify-between items-center text-sm border-l-2 border-red-500/30 pl-2">
                 <div>
                    <span className="font-semibold text-slate-200">{p.name}</span>
                    <span className="text-[10px] text-slate-500 ml-2">{p.team}</span>
                 </div>
                 <div className="text-right flex items-center gap-2 max-w-[50%]">
                    <span className="text-[9px] text-slate-400 text-right leading-tight" title={p.news}>{p.news}</span>
                    <span className="text-[10px] text-red-400 font-bold bg-red-500/10 px-1 py-0.5 whitespace-nowrap">{p.status}</span>
                 </div>
              </div>
            ))}
          </div>
        </div>

        {/* League Leaders (Stats) */}
        <div className="border border-slate-800 bg-[#0E121C] p-4 lg:col-span-2 h-64 overflow-y-auto custom-scrollbar">
          <h3 className="text-[10px] text-cyan-400 uppercase tracking-widest border-b border-slate-800 pb-2 mb-3 sticky top-0 bg-[#0E121C] z-10">League Leaders</h3>
          
          <div className="grid grid-cols-2 gap-6">
            <StatList title="Most Assists" data={intel.leaders.assists} />
            <StatList title="Goals + Assists" data={intel.leaders.goals_assists} />
            <StatList title="Match Rating (ICT)" data={intel.leaders.ict_index} />
            <StatList title="Expected Goals (xG)" data={intel.leaders.xg} />
            <StatList title="Expected Assists (xA)" data={intel.leaders.xa} />
            <StatList title="Most Tackles" data={intel.leaders.tackles} />
            <StatList title="Most Saves" data={intel.leaders.saves} />
            <StatList title="Minutes Played" data={intel.leaders.minutes} />
          </div>
        </div>

        {/* Team Specifics */}
        <div className="border border-slate-800 bg-[#0E121C] p-4 lg:col-span-4 max-h-80 overflow-y-auto custom-scrollbar">
          <h3 className="text-[10px] text-amber-400 uppercase tracking-widest border-b border-slate-800 pb-2 mb-3 sticky top-0 bg-[#0E121C] z-10">Team Specialists</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
             {intel.teams.map((t, i) => (
                <div key={i} className="bg-slate-900/50 p-3 border border-slate-800/50 rounded-sm hover:border-slate-600 transition-colors">
                   <h4 className="text-sm font-bold text-slate-200 mb-2 pb-1 border-b border-slate-800/50">{t.team_name}</h4>
                   <div className="space-y-1 text-xs">
                      <div className="flex justify-between"><span className="text-slate-500">Top Scorer:</span><span className="text-amber-400 font-semibold">{t.top_scorer}</span></div>
                      <div className="flex justify-between"><span className="text-slate-500">Top Assister:</span><span className="text-cyan-400 font-semibold">{t.top_assister}</span></div>
                      <div className="flex justify-between"><span className="text-slate-500">Top G+A:</span><span className="text-emerald-400 font-semibold">{t.top_ga}</span></div>
                      <div className="flex justify-between"><span className="text-slate-500">Penalties:</span><span className="text-slate-300 truncate max-w-[120px] text-right" title={t.pens}>{t.pens}</span></div>
                      <div className="flex justify-between"><span className="text-slate-500">Free Kicks:</span><span className="text-slate-300 truncate max-w-[120px] text-right" title={t.fks}>{t.fks}</span></div>
                   </div>
                </div>
             ))}
          </div>
        </div>

      </div>
    </div>
  );
}

function StatList({ title, data }) {
  return (
    <div>
      <h4 className="text-[10px] text-slate-500 uppercase tracking-widest mb-2 border-b border-slate-800/50 pb-1">{title}</h4>
      <div className="space-y-1 text-sm">
        {data.map((p, i) => (
          <div key={i} className="flex justify-between items-center group">
            <span className="text-slate-400 group-hover:text-slate-200 transition-colors truncate max-w-[100px]">{p.name}</span>
            <span className="text-cyan-400 font-mono text-xs">{p.val}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function TrendingHub({ trendingPlayers }) {
  if (!trendingPlayers || trendingPlayers.length === 0) return null;
  return (
    <div className="mt-8 border border-slate-800 bg-[#0E121C]">
      <div className="px-4 py-3 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
        <h2 className="text-sm font-bold text-amber-500 tracking-widest uppercase flex items-center gap-2">
           🔥 Global Market Sentiment (r/soccer & r/FantasyPL)
        </h2>
      </div>
      <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {trendingPlayers.map(p => (
          <div key={p.id} className="border border-slate-800 bg-slate-900/50 p-3 flex flex-col gap-2 hover:border-amber-500/50 transition-colors">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="font-bold text-white text-sm">{p.name}</span>
              <span className="text-[10px] font-mono bg-amber-500/20 text-amber-500 px-1.5 py-0.5 border border-amber-500/50">
                HYPE: {p.hype_score}/10
              </span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed italic">"{p.reason}"</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function SeasonTimeline({ timeline, targetGw }) {
  if (!timeline) return null;
  
  const teams = Object.keys(timeline).sort();
  const gameweeks = Array.from({ length: 38 }, (_, i) => i + 1);
  
  // Create a ref for horizontal scrolling to the target gameweek
  const scrollRef = useRef(null);
  
  useEffect(() => {
    if (scrollRef.current && targetGw) {
      // Approximate scroll position (each column is roughly 80px wide)
      const scrollPos = (targetGw - 3) * 80;
      scrollRef.current.scrollLeft = Math.max(0, scrollPos);
    }
  }, [targetGw, timeline]);

  return (
    <div className="mt-12 border border-slate-800 bg-[#0E121C]">
      <div className="px-4 py-3 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
        <h2 className="text-sm font-bold text-white tracking-widest uppercase flex items-center gap-2">
           <svg className="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
           Season Fixture Matrix
        </h2>
        <div className="flex gap-4 text-[10px] font-bold tracking-widest uppercase">
           <div className="flex items-center gap-1"><span className="w-2 h-2 bg-amber-500/20 border border-amber-500"></span> Double GW</div>
           <div className="flex items-center gap-1"><span className="w-2 h-2 bg-red-500/20 border border-red-500"></span> Blank GW</div>
        </div>
      </div>
      
      <div 
        ref={scrollRef}
        className="overflow-x-auto custom-scrollbar"
        style={{ scrollBehavior: 'smooth' }}
      >
        <table className="w-full text-left border-collapse min-w-max">
          <thead>
            <tr>
              <th className="sticky left-0 z-20 bg-[#0E121C] p-3 border-b border-r border-slate-800 text-[10px] text-slate-500 uppercase font-bold tracking-wider w-24 shadow-[4px_0_12px_rgba(0,0,0,0.5)]">Team</th>
              {gameweeks.map(gw => (
                <th key={gw} className={`p-2 border-b border-r border-slate-800/50 text-center text-[10px] uppercase font-bold tracking-wider min-w-[80px] ${gw === targetGw ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'text-slate-500'}`}>
                  GW{gw}
                  {gw === targetGw && <span className="block text-[8px] mt-0.5">NEXT</span>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {teams.map(team => (
              <tr key={team} className="hover:bg-slate-800/20 transition-colors">
                <td className="sticky left-0 z-10 bg-[#0E121C] p-3 border-b border-r border-slate-800 font-bold text-slate-300 text-xs shadow-[4px_0_12px_rgba(0,0,0,0.5)]">
                  {team}
                </td>
                {gameweeks.map(gw => {
                  const fixtures = timeline[team][gw] || [];
                  const isBlank = fixtures.length === 0;
                  const isDouble = fixtures.length > 1;
                  const isTarget = gw === targetGw;
                  
                  let cellClass = "p-2 border-b border-r border-slate-800/50 text-center text-[9px] relative ";
                  if (isBlank) cellClass += "bg-red-500/10 text-red-400/80 ";
                  else if (isDouble) cellClass += "bg-amber-500/10 text-amber-400 ";
                  else if (isTarget) cellClass += "bg-emerald-500/5 text-slate-300 ";
                  else cellClass += "text-slate-400 ";
                  
                  return (
                    <td key={`${team}-${gw}`} className={cellClass}>
                      {isBlank && <span className="font-bold opacity-50">BLANK</span>}
                      {!isBlank && (
                        <div className="flex flex-col gap-1">
                          {fixtures.map((fix, i) => (
                            <span key={i} className={`block ${isDouble ? 'border-b border-amber-500/20 pb-0.5 last:border-0 last:pb-0' : ''}`}>
                              {fix.replace('vs ', '').replace(' (H)', '(H)').replace(' (A)', '(A)')}
                            </span>
                          ))}
                        </div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
