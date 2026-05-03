import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [scoutData, setScoutData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const scoutResponse = await fetch(`${apiUrl}/api/scout-report`);
        
        if (!scoutResponse.ok) {
          throw new Error('Failed to fetch data from backend');
        }
        
        const scout = await scoutResponse.json();
        setScoutData(scout);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-[#0A0D14] text-slate-300 font-mono p-4 md:p-8 selection:bg-emerald-500/30">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="border-b border-slate-800 pb-6 mb-8 flex flex-col md:flex-row justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">FPL_AGENT_TERMINAL</h1>
            <p className="text-slate-500 text-sm mt-1">ADVANCED ANALYTICS & STRATEGY PROTOCOL</p>
          </div>
          {scoutData && (
            <div className="text-right mt-4 md:mt-0 flex flex-wrap gap-6">
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
            <p className="text-emerald-500 animate-pulse">INITIATING DATA FETCH...</p>
          </div>
        )}

        {error && (
          <div className="border-l-2 border-red-500 bg-red-500/10 p-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {scoutData && (
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

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border border-slate-800 bg-[#0E121C] p-4">
                    <div className="flex justify-between items-end mb-4 border-b border-slate-800 pb-2">
                      <h2 className="text-xs text-slate-500 uppercase tracking-widest">Optimized Starting XI</h2>
                      <span className="text-[10px] text-emerald-500 font-bold tracking-widest bg-emerald-500/10 px-2 py-0.5 border border-emerald-500/20">AUTO-CAPTAIN ENABLED</span>
                    </div>
                    <div className="space-y-1">
                      {scoutData.optimal_lineup.filter(p => p.status === 'Starting').map((player, idx) => (
                        <PlayerRow key={idx} player={player} />
                      ))}
                    </div>
                  </div>

                  <div className="border border-slate-800 bg-[#0E121C] p-4 h-fit">
                    <div className="flex justify-between items-end mb-4 border-b border-slate-800 pb-2">
                      <h2 className="text-xs text-slate-500 uppercase tracking-widest">Optimized Bench</h2>
                      <span className="text-[10px] text-slate-500 font-bold tracking-widest">ORDERED BY EP</span>
                    </div>
                    <div className="space-y-1">
                      {scoutData.optimal_lineup.filter(p => p.status === 'Bench').map((player, idx) => (
                        <PlayerRow key={idx} player={player} isBench benchOrder={idx + 1} />
                      ))}
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
                    <ActionPlanCard key={idx} plan={plan} idx={idx} />
                  ))}
                  {scoutData.action_plans.length === 0 && (
                     <p className="text-sm text-slate-500 italic">No favorable transfers found.</p>
                  )}
                </div>
              </div>

            </div>

            {/* League Intel Bottom Hub */}
            <LeagueIntel intel={scoutData.league_intel} />

          </div>
        )}
      </div>
    </div>
  );
}

function PlayerRow({ player, isBench, benchOrder }) {
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
          </span>
          {player.injury_warning && (
            <span className="text-[9px] text-red-400 mt-0.5" title={player.injury_warning}>
              ⚠️ {player.injury_warning}
            </span>
          )}
        </div>
      </div>
      <div className="text-right flex items-center gap-3">
         <span className="text-[10px] text-slate-600 uppercase">EP {player.ep_next}</span>
         {player.role_display === '(C)' && (
           <span className="text-[10px] text-emerald-400 font-bold border border-emerald-500/30 px-1 py-0.5">{(player.ep_next * 2).toFixed(1)}</span>
         )}
      </div>
    </div>
  );
}

function ActionPlanCard({ plan, idx }) {
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
              {plan.buy.map(p => (
                <div key={p} className="text-sm text-white font-semibold border-l border-emerald-500/50 pl-2 py-0.5">{p}</div>
              ))}
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
          <h3 className="text-[10px] text-red-400 uppercase tracking-widest border-b border-slate-800 pb-2 mb-3 sticky top-0 bg-[#0E121C]">Injury Ward (Top Owned)</h3>
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
          <h3 className="text-[10px] text-cyan-400 uppercase tracking-widest border-b border-slate-800 pb-2 mb-3 sticky top-0 bg-[#0E121C]">League Leaders</h3>
          
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
          <h3 className="text-[10px] text-amber-400 uppercase tracking-widest border-b border-slate-800 pb-2 mb-3 sticky top-0 bg-[#0E121C]">Team Specialists</h3>
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

export default App;
