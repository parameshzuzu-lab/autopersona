import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  Building2,
  TrendingUp,
  AlertTriangle,
  History,
  Tag,
  BookOpen
} from 'lucide-react';
import { GlassCard } from '../components/common/GlassCard';
import { MemoryOverview } from '../types';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

interface MemoryPageProps {
  memory?: MemoryOverview;
}

export const MemoryPage: React.FC<MemoryPageProps> = ({ memory }) => {
  const [activeTab, setActiveTab] = useState<'companies' | 'trends' | 'phrases' | 'opinions'>('companies');

  const companies = memory?.discussed_companies || [
    { company: 'Google DeepMind', mentions: 8 },
    { company: 'Anthropic', mentions: 6 },
    { company: 'Meta AI', mentions: 5 },
    { company: 'OpenAI', mentions: 4 },
    { company: 'NVIDIA', mentions: 3 }
  ];

  const trends = memory?.recent_trends || [
    { trend: 'Agentic Reasoning', frequency: 12 },
    { trend: 'GraphRAG Indexing', frequency: 9 },
    { trend: 'Open Source MoE', frequency: 7 },
    { trend: 'Sub-50ms Latency', frequency: 5 },
    { trend: 'NVLink 5 Scaling', frequency: 3 }
  ];

  const phrases = memory?.repeated_phrases || [
    "Game changer",
    "In today's fast-paced world",
    "Unraveling the future",
    "Mind-blowing revolution"
  ];

  const opinions = memory?.editorial_opinions || [
    "Open-source weights and MoE architectures are outpacing closed API models on engineering benchmarks.",
    "System latency and tool-use safety matter more than raw parameter counts for production RAG.",
    "Agentic workflows require graph memory state persistence, not naive vector chunking."
  ];

  const topicFrequency = memory?.topic_frequency || [
    { category: 'Agentic Systems', count: 14 },
    { category: 'LLM Infrastructure', count: 11 },
    { category: 'RAG & Graph Memory', count: 8 },
    { category: 'Hardware & Compute', count: 5 },
    { category: 'AI Governance', count: 3 }
  ];

  const COLORS = ['#38bdf8', '#818cf8', '#a855f7', '#34d399', '#f43f5e'];

  return (
    <div className="space-y-8 pb-16">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-3">
          <Brain className="w-7 h-7 text-purple-400" />
          <span>6-Dimensional Persona Memory Engine</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Historical post memory, company mention tracking, overused phrase filters, and persistent editorial opinions.
        </p>
      </div>

      {/* Top 4 Memory KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <GlassCard className="border-purple-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-medium">Remembered Concepts</p>
              <h3 className="text-3xl font-extrabold text-white mt-1">{memory?.past_posts_count || 42}</h3>
            </div>
            <BookOpen className="w-6 h-6 text-purple-400" />
          </div>
          <p className="text-[11px] text-purple-300 mt-3 font-mono">Indexed in PostgreSQL</p>
        </GlassCard>

        <GlassCard className="border-cyan-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-medium">Tracked Companies</p>
              <h3 className="text-3xl font-extrabold text-white mt-1">{companies.length}</h3>
            </div>
            <Building2 className="w-6 h-6 text-cyan-400" />
          </div>
          <p className="text-[11px] text-cyan-300 mt-3 font-mono">Deduplication active</p>
        </GlassCard>

        <GlassCard className="border-emerald-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-medium">Active AI Trends</p>
              <h3 className="text-3xl font-extrabold text-white mt-1">{trends.length}</h3>
            </div>
            <TrendingUp className="w-6 h-6 text-emerald-400" />
          </div>
          <p className="text-[11px] text-emerald-300 mt-3 font-mono">Trend frequency tracking</p>
        </GlassCard>

        <GlassCard className="border-amber-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-medium">Overused Phrases Blocked</p>
              <h3 className="text-3xl font-extrabold text-white mt-1">{phrases.length}</h3>
            </div>
            <AlertTriangle className="w-6 h-6 text-amber-400" />
          </div>
          <p className="text-[11px] text-amber-300 mt-3 font-mono">Avoided in AI Writer</p>
        </GlassCard>
      </div>

      {/* Main Grid: Chart + Tabbed Memory Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recharts Topic Frequency Visualization */}
        <GlassCard className="lg:col-span-2 space-y-6 border-purple-500/20">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white">Topic Frequency Distribution</h3>
              <p className="text-xs text-slate-400">Coverage breakdown across technical categories</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topicFrequency}>
                <XAxis dataKey="category" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }} />
                <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                  {topicFrequency.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Tabbed Memory Viewer */}
        <GlassCard className="space-y-6">
          {/* Tabs header */}
          <div className="flex items-center space-x-1 border-b border-slate-800 pb-3 text-xs font-medium">
            <button
              onClick={() => setActiveTab('companies')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'companies' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Companies
            </button>
            <button
              onClick={() => setActiveTab('trends')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'trends' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Trends
            </button>
            <button
              onClick={() => setActiveTab('phrases')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'phrases' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Phrases
            </button>
            <button
              onClick={() => setActiveTab('opinions')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'opinions' ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Opinions
            </button>
          </div>

          {/* Tab contents */}
          <div className="space-y-3">
            {activeTab === 'companies' && (
              <div className="space-y-2">
                {companies.map((c, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
                    <span className="font-semibold text-slate-200">{c.company}</span>
                    <span className="px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 font-mono text-[11px]">
                      {c.mentions} posts
                    </span>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'trends' && (
              <div className="space-y-2">
                {trends.map((t, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
                    <span className="font-semibold text-slate-200">{t.trend}</span>
                    <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 font-mono text-[11px]">
                      Freq: {t.frequency}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'phrases' && (
              <div className="space-y-2">
                <p className="text-[11px] text-slate-400">Phrases explicitly blocked to ensure editorial freshness:</p>
                {phrases.map((p, i) => (
                  <div key={i} className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs font-mono">
                    🚫 "{p}"
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'opinions' && (
              <div className="space-y-3">
                {opinions.map((o, i) => (
                  <div key={i} className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-200 text-xs leading-relaxed">
                    💡 "{o}"
                  </div>
                ))}
              </div>
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
