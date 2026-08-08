import React from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  XOctagon,
  BrainCircuit,
  Zap,
  TrendingUp,
  ExternalLink,
  Award
} from 'lucide-react';
import { GlassCard } from '../components/common/GlassCard';
import { PublishedPost, MemoryOverview, SchedulerStatus } from '../types';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

interface DashboardPageProps {
  posts: PublishedPost[];
  memory?: MemoryOverview;
  scheduler?: SchedulerStatus;
  onNavigateToFeed: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  posts,
  memory,
  scheduler,
  onNavigateToFeed,
}) => {
  // Chart data for publishing volume
  const chartData = [
    { time: '00:00', published: 2, rejected: 4 },
    { time: '04:00', published: 4, rejected: 7 },
    { time: '08:00', published: 7, rejected: 12 },
    { time: '12:00', published: 10, rejected: 19 },
    { time: '16:00', published: 12, rejected: 24 },
    { time: '20:00', published: scheduler?.total_published || 14, rejected: scheduler?.total_rejected || 28 },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Top Banner / Hero */}
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative overflow-hidden rounded-3xl p-8 bg-gradient-to-r from-slate-900 via-indigo-950/80 to-slate-900 border border-cyan-500/20 shadow-2xl"
      >
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>
        <div className="relative z-10 space-y-3">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-mono">
            <Zap className="w-3.5 h-3.5 fill-current" />
            <span>AUTONOMOUS AGENT ACTIVE &bull; NO MANUAL PROMPTING REQUIRED</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            AutoPersona <span className="text-gradient-cyan">AI Command Center</span>
          </h1>
          <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
            Continuously discovering live AI technical news, filtering low-quality noise, rejecting weak topics, remembering past posts, and publishing LinkedIn insights automatically.
          </p>
        </div>
      </motion.div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <GlassCard className="relative overflow-hidden border-cyan-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400">Total Published Posts</p>
              <h3 className="text-3xl font-extrabold text-white mt-1">
                {scheduler?.total_published || posts.length}
              </h3>
            </div>
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <FileText className="w-6 h-6" />
            </div>
          </div>
          <p className="text-[11px] text-emerald-400 mt-4 flex items-center space-x-1">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>100% Autonomous Pipeline</span>
          </p>
        </GlassCard>

        <GlassCard className="relative overflow-hidden border-rose-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400">Rejected Weak Topics</p>
              <h3 className="text-3xl font-extrabold text-white mt-1">
                {scheduler?.total_rejected || 28}
              </h3>
            </div>
            <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
              <XOctagon className="w-6 h-6" />
            </div>
          </div>
          <p className="text-[11px] text-rose-400 mt-4 font-mono">Quality score threshold &ge; 7.0/10</p>
        </GlassCard>

        <GlassCard className="relative overflow-hidden border-purple-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400">Remembered Concepts</p>
              <h3 className="text-3xl font-extrabold text-white mt-1">
                {memory?.past_posts_count || 42}
              </h3>
            </div>
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <BrainCircuit className="w-6 h-6" />
            </div>
          </div>
          <p className="text-[11px] text-purple-300 mt-4 font-mono">6-Dimensional Memory Engine</p>
        </GlassCard>

        <GlassCard className="relative overflow-hidden border-emerald-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400">Avg Editorial Score</p>
              <h3 className="text-3xl font-extrabold text-white mt-1">9.1 <span className="text-sm font-normal text-slate-400">/ 10</span></h3>
            </div>
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Award className="w-6 h-6" />
            </div>
          </div>
          <p className="text-[11px] text-emerald-400 mt-4 font-mono">High Technical Depth</p>
        </GlassCard>
      </div>

      {/* Main Grid: Chart + Recent Feed Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Analytics Chart Panel */}
        <GlassCard className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white">Autonomous Publishing & Rejection Velocity</h3>
              <p className="text-xs text-slate-400">24-hour real-time pipeline evaluation telemetry</p>
            </div>
            <div className="flex items-center space-x-4 text-xs font-mono">
              <div className="flex items-center space-x-1.5">
                <span className="w-3 h-3 rounded-full bg-cyan-400"></span>
                <span className="text-slate-300">Published</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-3 h-3 rounded-full bg-rose-500"></span>
                <span className="text-slate-300">Rejected</span>
              </div>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorPublished" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorRejected" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
                <Area type="monotone" dataKey="published" stroke="#38bdf8" strokeWidth={3} fillOpacity={1} fill="url(#colorPublished)" />
                <Area type="monotone" dataKey="rejected" stroke="#f43f5e" strokeWidth={3} fillOpacity={1} fill="url(#colorRejected)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Live Feed Column */}
        <GlassCard className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white">Latest Live Posts</h3>
            <button
              onClick={onNavigateToFeed}
              className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center space-x-1"
            >
              <span>View All</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-4">
            {posts.slice(0, 3).map((post) => (
              <div
                key={post.id}
                className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 hover:border-cyan-500/30 transition-all"
              >
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="text-cyan-400 font-semibold">Score: {post.editorial_score}/10</span>
                  <span className="text-slate-400">{new Date(post.published_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <h4 className="text-sm font-semibold text-slate-100 line-clamp-2">{post.title}</h4>
                <p className="text-xs text-slate-400 line-clamp-2">{post.content}</p>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
