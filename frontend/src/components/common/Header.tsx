import React from 'react';
import { Bot, Radio, Clock, ShieldCheck } from 'lucide-react';
import { Persona, SchedulerStatus } from '../../types';

interface HeaderProps {
  persona?: Persona;
  scheduler?: SchedulerStatus;
}

export const Header: React.FC<HeaderProps> = ({ persona, scheduler }) => {
  return (
    <header className="h-20 bg-[#0B0F19]/60 backdrop-blur-xl border-b border-slate-800/80 px-8 flex items-center justify-between sticky top-0 z-30">
      {/* Active Persona Badge */}
      <div className="flex items-center space-x-4">
        <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 flex items-center justify-center">
          <Bot className="w-6 h-6 text-indigo-400" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="font-bold text-slate-100 text-base">{persona?.name || 'AutoPersona AI'}</h2>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Executive AI Voice
            </span>
          </div>
          <p className="text-xs text-slate-400 truncate max-w-md">
            {persona?.editorial_voice || 'Authoritative, vision-driven AI researcher and strategist.'}
          </p>
        </div>
      </div>

      {/* Realtime Live Engine Badge */}
      <div className="flex items-center space-x-6 text-xs">
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono">
          <Radio className="w-3.5 h-3.5 animate-pulse" />
          <span>LIVE AUTONOMOUS AGENT</span>
        </div>

        <div className="flex items-center space-x-2 text-slate-400 font-mono">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          <span>
            Status: <strong className="text-cyan-400 uppercase">{scheduler?.status || 'RUNNING'}</strong>
          </span>
        </div>

        <div className="flex items-center space-x-1 text-slate-400">
          <ShieldCheck className="w-4 h-4 text-purple-400" />
          <span className="text-slate-300 font-medium">Quality Filter: &ge; {persona?.min_quality_score || 7.0}/10</span>
        </div>
      </div>
    </header>
  );
};
