import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, Bot, CheckCircle2, Database, Loader2, Radio, Server, Terminal, TimerReset } from 'lucide-react';
import { GlassCard } from '../components/common/GlassCard';
import { ActivityMonitor, apiService } from '../services/api';

const healthTone = (status: string) => status === 'healthy' || status === 'running' ? 'emerald' : status === 'degraded' ? 'amber' : 'rose';
const toneClasses = {
  emerald: { glow: 'bg-emerald-400/10', icon: 'text-emerald-300', dot: 'bg-emerald-400' },
  amber: { glow: 'bg-amber-400/10', icon: 'text-amber-300', dot: 'bg-amber-400' },
  rose: { glow: 'bg-rose-400/10', icon: 'text-rose-300', dot: 'bg-rose-400' },
};

export function ActivityMonitorPage() {
  const [monitor, setMonitor] = useState<ActivityMonitor>();
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [error, setError] = useState(false);

  useEffect(() => {
    const load = async () => { try { setMonitor(await apiService.getActivity()); setLastUpdated(new Date()); setError(false); } catch { setError(true); } };
    void load();
    const interval = window.setInterval(() => void load(), 5000);
    return () => window.clearInterval(interval);
  }, []);

  const stages = useMemo(() => monitor?.pipeline ?? [
    { label: 'Discovery', detail: 'Scanning subscribed sources', state: 'complete' },
    { label: 'Evaluation', detail: 'Ranking technical substance', state: 'active' },
    { label: 'Writing', detail: 'Waiting for selected topic', state: 'waiting' },
    { label: 'Publishing', detail: 'Queue is clear', state: 'waiting' },
  ], [monitor]);

  const services = [
    { label: 'Scheduler', value: monitor?.scheduler_running ? 'Running' : 'Paused', icon: TimerReset, status: monitor?.scheduler_running ? 'running' : 'degraded' },
    { label: 'Database', value: monitor?.database_status ?? 'Checking', icon: Database, status: monitor?.database_status ?? 'healthy' },
    { label: 'REST API', value: monitor?.api_status ?? 'Checking', icon: Server, status: monitor?.api_status ?? 'healthy' },
  ];

  return <div className="space-y-7 pb-12">
    <section className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between"><div><div className="mb-3 flex items-center gap-2 text-emerald-300"><Radio className="h-5 w-5 animate-pulse" /><span className="text-xs font-mono uppercase tracking-[0.18em]">Live operations</span></div><h1 className="text-3xl font-bold tracking-tight text-white">Activity monitor</h1><p className="mt-2 text-sm text-slate-400">A real-time view of the autonomous editorial loop and its infrastructure.</p></div><p className="text-xs font-mono text-slate-500">REFRESHED {lastUpdated.toLocaleTimeString()}</p></section>
    {error && <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">Live telemetry is temporarily unavailable. Retrying automatically.</div>}
    <div className="grid gap-5 md:grid-cols-3">{services.map(({ label, value, icon: Icon, status }) => { const tone = healthTone(status); const styles = toneClasses[tone]; return <GlassCard key={label} className="relative overflow-hidden p-5"><div className={`absolute right-0 top-0 h-20 w-20 rounded-full blur-2xl ${styles.glow}`} /><div className="flex items-start justify-between"><div><p className="text-xs font-medium text-slate-400">{label}</p><p className="mt-2 text-xl font-bold text-white">{value}</p></div><Icon className={`h-5 w-5 ${styles.icon}`} /></div><div className="mt-5 flex items-center gap-2 text-[11px] font-mono text-slate-500"><span className={`h-2 w-2 rounded-full ${styles.dot} ${tone === 'emerald' ? 'animate-pulse' : ''}`} />STATUS CHECKED</div></GlassCard>; })}</div>
    <div className="grid gap-6 xl:grid-cols-[1.1fr_.9fr]">
      <GlassCard className="p-6"><div className="mb-7 flex items-center justify-between"><div><h2 className="font-semibold text-white">Current cycle</h2><p className="mt-1 text-xs text-slate-400">Each stage updates as the loop moves forward.</p></div><Activity className="h-5 w-5 text-cyan-400" /></div><div className="space-y-0">{stages.map((stage, index) => <div key={stage.label} className="relative flex gap-4 pb-7 last:pb-0"><div className="relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-slate-700 bg-slate-900">{stage.state === 'active' ? <Loader2 className="h-4 w-4 animate-spin text-cyan-300" /> : stage.state === 'complete' ? <CheckCircle2 className="h-4 w-4 text-emerald-300" /> : <span className="h-2 w-2 rounded-full bg-slate-600" />}</div>{index < stages.length - 1 && <div className="absolute left-[17px] top-9 h-[calc(100%-18px)] w-px bg-slate-800" />}<div className="pt-1"><div className="flex items-center gap-2"><h3 className="text-sm font-medium text-slate-100">{stage.label}</h3><span className={`rounded-full px-2 py-0.5 text-[10px] font-mono ${stage.state === 'active' ? 'bg-cyan-500/10 text-cyan-300' : 'bg-slate-800 text-slate-400'}`}>{stage.state.toUpperCase()}</span></div><p className="mt-1 text-xs text-slate-400">{stage.detail}</p></div></div>)}</div></GlassCard>
      <GlassCard className="p-6"><div className="mb-5 flex items-center justify-between"><div><h2 className="font-semibold text-white">System journal</h2><p className="mt-1 text-xs text-slate-400">Streaming execution events</p></div><Terminal className="h-5 w-5 text-purple-400" /></div><div className="max-h-[340px] space-y-3 overflow-auto font-mono">{(monitor?.logs ?? []).map((log) => <motion.div key={log.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="border-l-2 border-slate-700 pl-3"><div className="flex gap-2 text-[10px]"><span className={log.level === 'ERROR' ? 'text-rose-300' : log.level === 'SUCCESS' ? 'text-emerald-300' : 'text-cyan-300'}>{log.level}</span><span className="text-slate-600">{new Date(log.created_at).toLocaleTimeString()}</span></div><p className="mt-1 text-xs leading-5 text-slate-300">{log.message}</p>{log.details && <p className="mt-1 text-[11px] leading-4 text-slate-500">{log.details}</p>}</motion.div>)}</div></GlassCard>
    </div>
    <GlassCard className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between"><div className="flex items-center gap-3"><Bot className="h-5 w-5 text-indigo-300" /><div><p className="text-sm font-medium text-slate-100">Current topic</p><p className="text-xs text-slate-400">{monitor?.current_topic ?? 'No topic is being processed.'}</p></div></div><div className="flex items-center gap-3"><span className="text-xs text-slate-500">Publishing progress</span><div className="h-2 w-40 overflow-hidden rounded-full bg-slate-800"><div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-indigo-400 transition-all duration-700" style={{ width: `${monitor?.publishing_progress ?? 0}%` }} /></div><span className="font-mono text-xs text-cyan-300">{monitor?.publishing_progress ?? 0}%</span></div></GlassCard>
  </div>;
}
