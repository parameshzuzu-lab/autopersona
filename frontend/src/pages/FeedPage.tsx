import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Share2,
  Copy,
  Check,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Award,
  Clock,
  CheckCircle2,
  Bot
} from 'lucide-react';
import { PublishedPost } from '../types';
import { GlassCard } from '../components/common/GlassCard';

interface FeedPageProps {
  posts: PublishedPost[];
  onLoadMore?: () => void;
  hasMore?: boolean;
}

export const FeedPage: React.FC<FeedPageProps> = ({ posts, onLoadMore, hasMore = true }) => {
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const [expandedRationaleId, setExpandedRationaleId] = useState<number | null>(null);

  const handleCopy = (id: number, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const toggleRationale = (id: number) => {
    setExpandedRationaleId(expandedRationaleId === id ? null : id);
  };

  return (
    <div className="space-y-8 pb-16 max-w-4xl mx-auto">
      {/* Header Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-3">
            <span>Autonomous Feed Stream</span>
            <span className="px-3 py-1 rounded-full text-xs font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              LinkedIn Editorial
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Curated, scored, and published automatically by the AI Persona on a 15-minute schedule.
          </p>
        </div>
      </div>

      {/* Feed Cards Stream */}
      <div className="space-y-6">
        <AnimatePresence>
          {posts.map((post, index) => (
            <motion.div
              key={post.id}
              initial={{ opacity: 0, y: 25 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.08 }}
            >
              <GlassCard className="p-7 space-y-6 relative overflow-hidden border-cyan-500/20 hover:border-cyan-500/40">
                {/* Post Top Bar: Persona Badge & Metadata Scores */}
                <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800/80">
                  {/* Persona Badge */}
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-black font-bold shadow-md shadow-cyan-500/20">
                      <Bot className="w-5 h-5 text-black" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-sm text-slate-100">AutoPersona AI</span>
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                          Executive AI Voice
                        </span>
                      </div>
                      <div className="flex items-center space-x-2 text-[11px] text-slate-400 font-mono">
                        <Clock className="w-3 h-3 text-cyan-400" />
                        <span>{new Date(post.published_at).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  {/* Editorial Score & Confidence Badges */}
                  <div className="flex items-center space-x-3 text-xs font-mono">
                    <div className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                      <Award className="w-3.5 h-3.5" />
                      <span>Editorial Score: <strong>{post.editorial_score}/10</strong></span>
                    </div>

                    <div className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-300">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Confidence: <strong>{Math.round((post.confidence_score || 0.94) * 100)}%</strong></span>
                    </div>
                  </div>
                </div>

                {/* Article Headline */}
                <h2 className="text-xl font-bold text-slate-50 tracking-tight leading-snug">
                  {post.title}
                </h2>

                {/* Article Body (LinkedIn Tone, <= 250 words) */}
                <div className="bg-slate-950/60 rounded-xl p-5 border border-slate-800/80 font-sans text-sm text-slate-200 leading-relaxed whitespace-pre-line">
                  {post.content}
                </div>

                {/* Hashtags & Copy Action */}
                <div className="flex items-center justify-between pt-2">
                  <div className="flex flex-wrap gap-2">
                    {(post.hashtags || ['#AI', '#SystemArchitecture', '#TechLeadership']).map((tag, i) => (
                      <span key={i} className="text-xs text-cyan-400/90 font-mono hover:underline cursor-pointer">
                        {tag}
                      </span>
                    ))}
                  </div>

                  <button
                    onClick={() => handleCopy(post.id, `${post.title}\n\n${post.content}`)}
                    className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-xs text-slate-200 border border-slate-700/80 transition-all"
                  >
                    {copiedId === post.id ? (
                      <>
                        <Check className="w-4 h-4 text-emerald-400" />
                        <span className="text-emerald-400">Copied to Clipboard!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4 text-slate-400" />
                        <span>Copy Post</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Publishing Rationale & Sources Drawer */}
                <div className="border-t border-slate-800/80 pt-4">
                  <button
                    onClick={() => toggleRationale(post.id)}
                    className="w-full flex items-center justify-between text-xs text-slate-400 hover:text-cyan-400 transition-colors font-mono py-1"
                  >
                    <span className="flex items-center space-x-2">
                      <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Why Selected & Publishing Rationale</span>
                    </span>
                    {expandedRationaleId === post.id ? (
                      <ChevronUp className="w-4 h-4" />
                    ) : (
                      <ChevronDown className="w-4 h-4" />
                    )}
                  </button>

                  {expandedRationaleId === post.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-3 space-y-3 bg-slate-900/90 rounded-xl p-4 border border-slate-800 text-xs space-y-2"
                    >
                      <div>
                        <span className="text-cyan-400 font-semibold uppercase block mb-1">Why Selected:</span>
                        <p className="text-slate-300">
                          {post.why_selected || `Selected due to high technical substance and alignment with active persona core topics.`}
                        </p>
                      </div>

                      <div>
                        <span className="text-purple-400 font-semibold uppercase block mb-1">Why Relevant Now:</span>
                        <p className="text-slate-300">
                          {post.why_relevant_now || `Critical industry timeliness as architecture shifts toward autonomous systems.`}
                        </p>
                      </div>

                      {post.source_urls && post.source_urls.length > 0 && (
                        <div>
                          <span className="text-emerald-400 font-semibold uppercase block mb-1">Sources & Verification URLs:</span>
                          <div className="space-y-1">
                            {post.source_urls.map((url, uidx) => (
                              <a
                                key={uidx}
                                href={url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-cyan-400 hover:underline flex items-center space-x-1.5 text-xs truncate max-w-lg"
                              >
                                <ExternalLink className="w-3.5 h-3.5 flex-shrink-0" />
                                <span className="truncate">{url}</span>
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Infinite Scroll / Load More Action */}
      {hasMore && (
        <div className="text-center pt-6">
          <button
            onClick={onLoadMore}
            className="px-8 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 text-sm font-semibold transition-all hover:border-cyan-500/40"
          >
            Load Older Feed Items
          </button>
        </div>
      )}
    </div>
  );
};
