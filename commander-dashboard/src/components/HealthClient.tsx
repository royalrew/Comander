"use client";

import React, { useState, useRef, useEffect } from 'react';
import { HeartPulse, Activity, Flame, UtilityPole, Send, Calendar, Battery, Zap } from 'lucide-react';
import AgentCard from '@/components/AgentCard';

const MessageContent = ({ text }: { text: string }) => {
    const jsonRegex = /```json\s*(\{[\s\S]*?\})\s*```/;
    const match = text.match(jsonRegex);

    if (match) {
        try {
            const data = JSON.parse(match[1]);
            if (data._ui_type === 'workout_card') {
                const textBefore = text.slice(0, match.index).trim();
                const textAfter = text.slice(match.index! + match[0].length).trim();
                return (
                    <div className="space-y-4">
                        {textBefore && <div className="whitespace-pre-wrap">{textBefore}</div>}
                        <div className="bg-black/60 border border-emerald-500/40 rounded-xl p-4 my-2 shadow-[0_0_15px_theme(colors.emerald.500/10)]">
                            <h3 className="text-emerald-400 font-bold mb-3 flex items-center gap-2">
                                <Flame size={18} />
                                {data.title}
                            </h3>
                            <div className="space-y-2">
                                {data.exercises?.map((ex: any, i: number) => (
                                    <div key={i} className="flex justify-between items-center bg-white/5 p-3 rounded-lg border border-white/5 hover:border-emerald-500/30 transition-colors">
                                        <div className="flex items-center gap-3">
                                            <input type="checkbox" className="w-4 h-4 rounded appearance-none border border-emerald-500/50 checked:bg-emerald-500 checked:border-emerald-500 cursor-pointer transition-all" />
                                            <span className="text-white font-medium text-sm">{ex.name}</span>
                                        </div>
                                        <span className="text-emerald-500 font-mono text-sm bg-emerald-500/10 px-2 py-0.5 rounded">{ex.sets}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                        {textAfter && <div className="whitespace-pre-wrap">{textAfter}</div>}
                    </div>
                );
            }
        } catch (e) {
            // fallback to original text if JSON fails to parse
        }
    }
    return <div className="whitespace-pre-wrap">{text}</div>;
};

export default function HealthClient() {
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState<any[]>([
        { role: 'assistant', text: "Reporting for duty. I've synced your latest CEO Profile and calendar. Ready to schedule your next Deep Work(out). What's the protocol today?" }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!query.trim() || isLoading) return;

        const userMsg = query;
        setQuery("");
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setIsLoading(true);

        const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://comander-production.up.railway.app";
        try {
            const res = await fetch(`${API_URL}/ask`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: userMsg, user_id: "Jimmy" })
            });

            if (res.ok) {
                const data = await res.json();
                setMessages(prev => [...prev, { role: 'assistant', text: data.response_text }]);
            } else {
                setMessages(prev => [...prev, { role: 'assistant', text: "Coach Error: System is currently resting. Try again." }]);
            }
        } catch (e) {
            setMessages(prev => [...prev, { role: 'assistant', text: "Coach Sync Error: Unable to reach the Command Center." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* The Readiness Hero (Glassmorphism) */}
            <div className="relative overflow-hidden p-8 glass rounded-3xl border border-emerald-500/20 bg-emerald-500/5">
                <div className="absolute top-0 right-0 p-8 opacity-10">
                    <Battery size={120} className="text-emerald-500" />
                </div>
                <div className="relative z-10 flex flex-col md:flex-row items-center gap-10">
                    {/* Gauge/Score */}
                    <div className="flex flex-col items-center justify-center w-40 h-40 rounded-full border-[6px] border-emerald-500/30 bg-black/40 shadow-[0_0_30px_theme(colors.emerald.500/20)]">
                        <span className="text-5xl font-black text-white tracking-tighter">84</span>
                        <span className="text-xs uppercase font-bold tracking-widest text-emerald-400 mt-1">Readiness</span>
                    </div>
                    {/* Text block */}
                    <div className="flex-1 text-center md:text-left">
                        <div className="inline-flex items-center gap-2 px-2 py-1 mb-3 text-[10px] font-bold tracking-widest uppercase rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                            <Zap size={12} /> Optimal Recovery
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Prime condition for a heavy lift.</h2>
                        <p className="text-zinc-400 max-w-lg">
                            Sleep quality was excellent (7h 45m). Resting heart rate is down to 48 bpm. The calendar shows a 90-minute gap at 14:30. Let's load the barbell.
                        </p>
                    </div>
                </div>
            </div>

            {/* Sub-metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <AgentCard
                    title="DAILY STEPS"
                    value="4,231"
                    subtitle="Goal: 10,000"
                    icon={<Activity size={24} />}
                />
                <AgentCard
                    title="SLEEP SCORE"
                    value="88"
                    subtitle="Oura Sync Status: Mocked"
                    icon={<UtilityPole size={24} />}
                />
                <AgentCard
                    title="ACTIVE CALORIES"
                    value="310 kcal"
                    subtitle="Goal: 700 kcal"
                    icon={<Flame size={24} />}
                />
            </div>

            {/* Lower Grid: The Coach Chat & The Battle Plan */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-auto">
                {/* The Coach Console */}
                <div className="glass rounded-3xl border border-white/5 p-6 flex flex-col h-[600px]">
                    <h2 className="text-xl font-bold flex items-center gap-3 text-white mb-6">
                        <HeartPulse className="text-emerald-500" />
                        The Coach Terminal
                    </h2>

                    {/* Chat Messages */}
                    <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 custom-scrollbar">
                        {messages.map((m, i) => (
                            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[85%] rounded-2xl p-4 text-sm ${m.role === 'user'
                                    ? 'bg-blue-600 outline-none text-white'
                                    : 'bg-black/40 border border-emerald-500/20 text-zinc-300 font-mono'
                                    }`}>
                                    <MessageContent text={m.text} />
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-black/40 border border-emerald-500/20 text-emerald-500 rounded-2xl p-4 text-sm font-mono flex items-center gap-3">
                                    <div className="flex gap-1">
                                        <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                    <span className="animate-pulse">Analyzing biometa...</span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Chat Input */}
                    <div className="relative mt-auto">
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSend();
                                }
                            }}
                            placeholder="Consult your coach..."
                            disabled={isLoading}
                            className="w-full bg-black/60 border border-white/10 rounded-2xl pl-4 pr-12 py-4 text-sm text-white focus:outline-none focus:border-emerald-500/50 resize-none h-[60px]"
                        />
                        <button
                            onClick={handleSend}
                            disabled={isLoading || !query.trim()}
                            className="absolute right-2 top-2 p-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-white/5 disabled:text-white/20 text-white rounded-xl transition-colors"
                        >
                            <Send size={16} />
                        </button>
                    </div>
                </div>

                {/* The Battle Plan */}
                <div className="glass rounded-3xl border border-white/5 p-6 flex flex-col h-[600px]">
                    <h2 className="text-xl font-bold flex items-center gap-3 text-white mb-6">
                        <Calendar className="text-blue-500" />
                        Weekly Battle Plan
                    </h2>

                    <div className="flex-1 overflow-y-auto pr-2">
                        <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-white/10 before:to-transparent">
                            {/* Dummy Timeline Items */}
                            <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                                <div className="flex items-center justify-center w-10 h-10 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                                    <Zap size={16} />
                                </div>
                                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-white/5 bg-black/40">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="font-bold text-emerald-400 text-sm">Today, 14:30</span>
                                    </div>
                                    <div className="text-white font-bold mb-1">Deep Work(out): Legs</div>
                                    <div className="text-xs text-zinc-400">Squats, Romanian Deadlifts, Bulgarian Split Squats. Scheduled during a 90m calendar gap.</div>
                                </div>
                            </div>

                            <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                                <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white/10 bg-black/40 text-zinc-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                                    <HeartPulse size={16} />
                                </div>
                                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-white/5 bg-white/5 opacity-50">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="font-bold text-zinc-400 text-sm">Tomorrow, 08:00</span>
                                    </div>
                                    <div className="text-white font-bold mb-1">Recovery Run (Zone 2)</div>
                                    <div className="text-xs text-zinc-400">45 minutes easy pace. Pre-meeting cardiovascular tune-up.</div>
                                </div>
                            </div>

                            <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                                <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white/10 bg-black/40 text-zinc-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                                    <Zap size={16} />
                                </div>
                                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-white/5 bg-white/5 opacity-50">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="font-bold text-zinc-400 text-sm">Thursday, 18:00</span>
                                    </div>
                                    <div className="text-white font-bold mb-1">Deep Work(out): Push</div>
                                    <div className="text-xs text-zinc-400">Overhead Press, Bench, Triceps. Scheduled immediately after your 17:00 Q3 Sync.</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
