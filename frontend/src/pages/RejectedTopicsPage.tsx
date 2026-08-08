import { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ExternalLink, Filter, Search, ShieldX, SlidersHorizontal } from 'lucide-react';
import { GlassCard } from '../components/common/GlassCard';
import { RejectedTopic } from '../types';
import { apiService } from '../services/api';

const reasonLabel = (reason: string) => {
  if (/duplicate/i.test(reason)) return 'Duplicate coverage';
  if (/clickbait/i.test(reason)) return 'Clickbait signal';
  if (/threshold|quality score|technical depth/i.test(reason)) return 'Below quality bar';
  return 'Editorial fit';
};

export function RejectedTopicsPage() {
  const [topics, setTopics] = useState<RejectedTopic[]>([]);
  const [selectedReason, setSelectedReason] = useState('All reasons');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiService.getTopics().then((data) => setTopics(data.rejected_topics)).finally(() => setLoading(false));
  }, []);

  const reasons = useMemo(() => ['All reasons', ...Array.from(new Set(topics.map((topic) => reasonLabel(topic.rejection_reason))))], [topics]);
  const visibleTopics = topics.filter((topic) =>
    (selectedReason === 'All reasons' || reasonLabel(topic.rejection_reason) === selectedReason)
    && `${topic.topic_title} ${topic.rejection_reason}`.toLowerCase().includes(query.toLowerCase()),
  );

  return <div className="space-y-7 pb-12">
    <section className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
      <div>
        <div className="mb-3 flex items-center gap-2 text-rose-300"><ShieldX className="h-5 w-5" /><span className="text-xs font-mono uppercase tracking-[0.18em]">Editorial boundary</span></div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Rejected topics</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-400">An audit trail for stories that did not meet the publication bar. Rejections preserve the decision, not just the outcome.</p>
      </div>
      <div className="rounded-2xl border border-rose-500/20 bg-rose-500/5 px-5 py-3 text-right"><p className="text-2xl font-bold text-rose-300">{topics.length}</p><p className="text-[11px] font-mono uppercase tracking-wider text-rose-200/70">topics withheld</p></div>
    </section>
    <GlassCard className="overflow-hidden p-0">
      <div className="flex flex-col gap-4 border-b border-slate-800/80 p-5 lg:flex-row lg:items-center lg:justify-between">
        <label className="flex min-w-0 flex-1 items-center gap-3 rounded-xl border border-slate-700/80 bg-slate-950/50 px-3 py-2.5 text-slate-400 focus-within:border-cyan-500/50"><Search className="h-4 w-4" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search headline or decision..." className="w-full bg-transparent text-sm text-slate-100 outline-none placeholder:text-slate-600" /></label>
        <div className="flex items-center gap-2 overflow-x-auto"><SlidersHorizontal className="h-4 w-4 shrink-0 text-slate-500" />{reasons.map((reason) => <button key={reason} onClick={() => setSelectedReason(reason)} className={`whitespace-nowrap rounded-lg px-3 py-2 text-xs transition ${selectedReason === reason ? 'bg-cyan-500/15 text-cyan-300 ring-1 ring-cyan-500/30' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}>{reason}</button>)}</div>
      </div>
      <div className="hidden grid-cols-[minmax(260px,2fr)_minmax(240px,1.5fr)_100px_135px_150px] gap-4 border-b border-slate-800/80 px-6 py-3 text-[10px] font-mono uppercase tracking-wider text-slate-500 md:grid"><span>Headline</span><span>Reason for rejection</span><span>Score</span><span>Date</span><span>Source</span></div>
      <AnimatePresence mode="popLayout">
        {visibleTopics.map((topic, index) => <motion.article key={topic.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }} className="grid gap-3 border-b border-slate-800/60 px-6 py-5 last:border-0 md:grid-cols-[minmax(260px,2fr)_minmax(240px,1.5fr)_100px_135px_150px] md:gap-4 md:items-center">
          <h2 className="text-sm font-semibold leading-5 text-slate-100">{topic.topic_title}</h2>
          <div><span className="mb-1 inline-block rounded-full bg-rose-500/10 px-2 py-0.5 text-[10px] font-medium text-rose-300">{reasonLabel(topic.rejection_reason)}</span><p className="line-clamp-2 text-xs leading-5 text-slate-400">{topic.rejection_reason}</p></div>
          <div className="font-mono text-sm"><span className={topic.quality_score < 5 ? 'text-rose-300' : 'text-amber-300'}>{topic.quality_score.toFixed(1)}</span><span className="text-slate-600"> / 10</span></div>
          <time className="text-xs text-slate-400">{new Date(topic.evaluated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</time>
          {topic.source_url ? <a href={topic.source_url} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 truncate text-xs text-cyan-400 hover:text-cyan-300"><ExternalLink className="h-3.5 w-3.5 shrink-0" /><span className="truncate">Open source</span></a> : <span className="text-xs text-slate-600">No source recorded</span>}
        </motion.article>)}
      </AnimatePresence>
      {!loading && visibleTopics.length === 0 && <div className="p-16 text-center"><Filter className="mx-auto mb-3 h-7 w-7 text-slate-600" /><p className="text-sm text-slate-400">No rejected topics match this filter.</p></div>}
    </GlassCard>
  </div>;
}
