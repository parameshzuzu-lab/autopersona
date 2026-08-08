import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Rss,
  Brain,
  XCircle,
  UserCheck,
  Settings,
  Terminal,
  Zap,
  Activity,
  Radio
} from 'lucide-react';

interface SidebarProps {
  onTriggerPublish: () => void;
  isPublishing: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ onTriggerPublish, isPublishing }) => {
  const navItems = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard },
    { label: 'Feed', path: '/feed', icon: Rss },
    { label: 'Memory Engine', path: '/memory', icon: Brain },
    { label: 'Rejected Topics', path: '/rejected', icon: XCircle },
    { label: 'Activity Monitor', path: '/activity', icon: Radio },
    { label: 'Persona Profile', path: '/persona', icon: UserCheck },
    { label: 'Settings', path: '/settings', icon: Settings },
    { label: 'System Logs', path: '/logs', icon: Terminal },
  ];

  return (
    <aside className="w-64 bg-[#0B0F19]/80 backdrop-blur-2xl border-r border-slate-800/80 flex flex-col justify-between p-5 min-h-screen sticky top-0 z-40">
      <div className="space-y-8">
        {/* Brand Header */}
        <div className="flex items-center space-x-3 px-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Zap className="w-6 h-6 text-black fill-current" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-wide text-gradient-cyan">AutoPersona</h1>
            <div className="flex items-center space-x-1.5 text-xs text-emerald-400 font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              <span>AUTONOMOUS</span>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-cyan-500/15 to-indigo-500/15 text-cyan-400 border border-cyan-500/30 shadow-[0_0_15px_rgba(34,211,238,0.1)]'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Manual Trigger Button & Status Panel */}
      <div className="space-y-4 pt-6 border-t border-slate-800/80">
        <button
          onClick={onTriggerPublish}
          disabled={isPublishing}
          className="w-full relative group overflow-hidden rounded-xl p-[1px] font-semibold text-sm transition-all duration-300 disabled:opacity-50"
        >
          <span className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-indigo-500 to-purple-600 rounded-xl"></span>
          <div className="relative bg-[#0F172A] rounded-[11px] px-4 py-3 flex items-center justify-center space-x-2 group-hover:bg-opacity-80 transition-all">
            <Activity className={`w-4 h-4 text-cyan-400 ${isPublishing ? 'animate-spin' : ''}`} />
            <span className="text-slate-100 font-medium">
              {isPublishing ? 'Publishing...' : 'Force Publish Run'}
            </span>
          </div>
        </button>

        <div className="px-3 py-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-400 font-mono flex items-center justify-between">
          <span>Interval:</span>
          <span className="text-cyan-400 font-semibold">Every 15 min</span>
        </div>
      </div>
    </aside>
  );
};
