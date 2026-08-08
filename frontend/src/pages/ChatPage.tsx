import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, Sparkles, MessageSquarePlus, Loader2, AlertTriangle } from 'lucide-react';
import { apiService } from '../services/api';
import { ChatMessage as ChatMessageType } from '../types';
import { MarkdownMessage } from '../components/common/MarkdownMessage';

const SUGGESTED_QUESTIONS = [
  'What is inheritance in Java?',
  'Calculate 25 * 16',
  'Who are you?',
  'Java inheritance na enna Tamil la sollu',
  'Give me a Java program for method overriding',
];

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [bannerError, setBannerError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const ask = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isTyping) return;

    const userMessage: ChatMessageType = { role: 'user', content: trimmed };
    const updated = [...messages, userMessage];
    setMessages(updated);
    setInput('');
    setBannerError(null);
    setIsTyping(true);

    try {
      const history = messages.slice(-10);
      const res = await apiService.askChat(trimmed, history);

      if (res.mode === 'error' && res.error) {
        setBannerError(res.error || 'The AI could not answer right now.');
        setMessages((prev) => [...prev, { role: 'assistant', content: res.reply }]);
      } else {
        setMessages((prev) => [...prev, { role: 'assistant', content: res.reply }]);
      }
    } catch (e) {
      setBannerError('Could not reach the AI service. Please check your connection and try again.');
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void ask(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void ask(input);
    }
  };

  const reset = () => {
    setMessages([]);
    setBannerError(null);
  };

  return (
    <div className="space-y-6 pb-16 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-3">
            <span>Persona Chat</span>
            <span className="px-3 py-1 rounded-full text-xs font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              Ask Anything
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Technical, factual, coding, math, and Tamil/Tanglish questions supported.
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={reset}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-xs text-slate-300 border border-slate-700/80 transition-all"
          >
            <MessageSquarePlus className="w-4 h-4 text-cyan-400" />
            <span>New Chat</span>
          </button>
        )}
      </div>

      {/* Chat Window */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800/80 flex flex-col" style={{ minHeight: '480px' }}>
        {/* Messages Scroll Area */}
        <div className="flex-1 space-y-5 overflow-y-auto pr-1" style={{ maxHeight: '560px' }}>
          {messages.length === 0 && (
            <div className="py-10 flex flex-col items-center text-center">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 mb-4">
                <Bot className="w-7 h-7 text-black" />
              </div>
              <h3 className="text-lg font-bold text-white">Ask anything</h3>
              <p className="text-xs text-slate-400 mt-1 max-w-sm">
                Coding, math, explanations, Tamil/Tanglish, or about the AutoPersona agent itself.
              </p>
              <div className="flex flex-wrap justify-center gap-2 mt-6">
                {SUGGESTED_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => void ask(q)}
                    className="px-4 py-2 rounded-xl bg-slate-900/70 border border-slate-800 text-xs text-slate-300 hover:border-cyan-500/40 hover:text-cyan-300 transition-all"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[88%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white rounded-br-md shadow-lg shadow-cyan-600/20 whitespace-pre-line'
                      : 'bg-slate-900/80 border border-slate-800 text-slate-200 rounded-bl-md'
                  }`}
                >
                  {msg.role === 'assistant' ? (
                    <MarkdownMessage content={msg.content} />
                  ) : (
                    msg.content
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isTyping && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
              <div className="flex items-center space-x-2 px-4 py-3 rounded-2xl bg-slate-900/80 border border-slate-800 text-slate-400 text-sm">
                <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />
                <span>Thinking…</span>
              </div>
            </motion.div>
          )}

          <div ref={bottomRef} />
        </div>

        {bannerError && (
          <div className="mt-3 px-4 py-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{bannerError}</span>
          </div>
        )}

        {/* Input Bar */}
        <form onSubmit={handleSubmit} className="mt-4 flex items-end space-x-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question… (Enter to send, Shift+Enter for newline)"
            disabled={isTyping}
            rows={Math.min(4, Math.max(1, input.split('\n').length))}
            className="flex-1 resize-none px-4 py-3 rounded-xl bg-slate-950/70 border border-slate-700/80 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 transition-all disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={isTyping || !input.trim()}
            className="relative group overflow-hidden rounded-xl p-[1px] font-semibold text-sm transition-all disabled:opacity-50"
          >
            <span className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-indigo-500 to-purple-600 rounded-xl"></span>
            <span className="relative bg-[#0F172A] rounded-[11px] px-5 py-3 flex items-center justify-center space-x-2">
              <Send className="w-4 h-4 text-cyan-400" />
              <span className="text-slate-100">{isTyping ? '…' : 'Send'}</span>
            </span>
          </button>
        </form>
      </div>

      {/* Footer note */}
      <div className="flex items-center justify-center space-x-2 text-[11px] text-slate-500 font-mono pt-1">
        <Sparkles className="w-3.5 h-3.5 text-cyan-500/70" />
        <span>Accuracy &gt; always-answering. The agent never fabricates facts.</span>
      </div>
    </div>
  );
};