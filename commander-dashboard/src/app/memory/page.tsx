"use client";

import React, { useEffect, useState } from 'react';
import { Database, Search, History, Trash2, ShieldAlert } from 'lucide-react';

export default function MemoryPage() {
    const [memories, setMemories] = useState<any[]>([]);
    const [status, setStatus] = useState<any>(null);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const fetchData = async () => {
        setIsRefreshing(true);
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://comander-production.up.railway.app';
        try {
            const [memRes, statusRes] = await Promise.all([
                fetch(`${API_URL}/api/v1/cortex/memories`),
                fetch(`${API_URL}/api/v1/cortex/status`),
            ]);

            if (memRes.ok) setMemories((await memRes.json()).memories || []);
            if (statusRes.ok) setStatus(await statusRes.json());
        } catch (err) {
            console.error(err);
        } finally {
            setIsRefreshing(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000); // 10s poll
        return () => clearInterval(interval);
    }, []);

    // Calculate memory percentage safely
    let memoryUsageStr = status?.memory_usage || "0/10000 vectors";
    let memoryCount = parseInt(memoryUsageStr.split("/")[0]) || 0;
    let maxMemory = parseInt(memoryUsageStr.split("/")[1]) || 10000;
    let memoryPercent = Math.min((memoryCount / maxMemory) * 100, 100).toFixed(1);

    return (
        <div className="space-y-8 animate-fade-in">
            <header className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight steel-text flex items-center gap-3">
                        <Database className="text-blue-500" size={32} />
                        Minne & Konvergens
                    </h1>
                    <p className="mt-2 text-muted-foreground">
                        Långtidsminne via OpenSearch och konversationshistorik via PostgreSQL.
                    </p>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={fetchData}
                        disabled={isRefreshing}
                        className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-xl border border-white/10 transition-colors text-sm font-medium disabled:opacity-50"
                    >
                        {isRefreshing ? <span className="animate-spin text-blue-400">↻</span> : <History size={16} className="text-blue-400" />}
                        {isRefreshing ? 'Uppdaterar...' : 'Synka'}
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-xl border border-white/10 transition-colors text-sm font-medium">
                        <Trash2 size={16} className="text-red-400" />
                        Rensa Cache
                    </button>
                </div>
            </header>

            {/* Global Search */}
            <div className="relative mb-8">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Search className="text-muted-foreground" size={20} />
                </div>
                <input
                    type="text"
                    placeholder="Sök i AI:ns minne (RAG Vectors)..."
                    className="w-full bg-black/40 border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-white outline-none focus:border-blue-500/50 shadow-[inset_0_2px_10px_rgba(0,0,0,0.5)] transition-all"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* RAG Database State */}
                <div className="lg:col-span-2 space-y-6">
                    <h2 className="text-xl font-bold steel-text flex items-center gap-2">
                        <History className="text-blue-400" size={20} />
                        Senaste Inlärning (OpenSearch)
                    </h2>

                    <div className="glass rounded-3xl border border-white/5 overflow-hidden">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-white/5 border-b border-white/10 uppercase text-[10px] tracking-widest text-muted-foreground">
                                <tr>
                                    <th className="px-6 py-4 font-bold">Innehåll</th>
                                    <th className="px-6 py-4 font-bold">Kategori</th>
                                    <th className="px-6 py-4 font-bold text-right">Tidpunkt</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5 text-gray-300">
                                {memories.map((mem, i) => (
                                    <tr key={i} className="hover:bg-white/5 transition-colors group">
                                        <td className="px-6 py-4 font-mono text-xs text-blue-200 truncate max-w-[200px]" title={mem.text}>
                                            {mem.text}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded-md text-[10px] uppercase font-bold tracking-wider">
                                                {mem.category || 'Generell'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right text-muted-foreground text-xs whitespace-nowrap">
                                            {new Date(mem.timestamp).toLocaleString("sv-SE", { dateStyle: "short", timeStyle: "medium" })}
                                        </td>
                                    </tr>
                                ))}
                                {memories.length === 0 && (
                                    <tr>
                                        <td colSpan={3} className="px-6 py-12 text-center text-muted-foreground">
                                            {status ? "Hittade inga sparade vektorer." : "Laddar minnen från Vector DB..."}
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* System Vitals & Stats */}
                <div className="space-y-6">
                    <h2 className="text-xl font-bold steel-text flex items-center gap-2">
                        <ShieldAlert className="text-emerald-400" size={20} />
                        Minnes-Hälsa
                    </h2>

                    <div className="p-6 glass rounded-3xl border border-white/5 space-y-6">
                        <div>
                            <div className="flex justify-between text-xs font-bold text-muted-foreground tracking-widest uppercase mb-2">
                                <span>OpenSearch Volym</span>
                                <span className={parseFloat(memoryPercent) > 80 ? "text-red-400" : "text-emerald-400"}>
                                    {memoryPercent}%
                                </span>
                            </div>
                            <div className="w-full h-2 rounded-full bg-black/50 overflow-hidden border border-white/5">
                                <div
                                    className={`h-full ${parseFloat(memoryPercent) > 80 ? 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]' : 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]'} rounded-full transition-all duration-1000`}
                                    style={{ width: `${memoryPercent}%` }}
                                ></div>
                            </div>
                            <p className="text-[10px] text-muted-foreground mt-2">{memoryCount} dokument indexerade (Max {maxMemory})</p>
                        </div>

                        <div className="pt-4 border-t border-white/10">
                            <div className="flex justify-between text-xs font-bold text-muted-foreground tracking-widest uppercase mb-2">
                                <span>Postgres Sessions</span>
                                <span className={status?.heartbeat === 'stable' ? "text-blue-400" : "text-amber-400"}>
                                    {status?.heartbeat === 'stable' ? 'Länkad / Aktiv' : 'Kopplar upp...'}
                                </span>
                            </div>
                            <p className="text-[10px] text-muted-foreground mt-2 leading-relaxed">
                                Telegram-historik bevaras löpande. Äldsta session: 3 dagar. Expungement policy körs inatt 04:00.
                            </p>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
