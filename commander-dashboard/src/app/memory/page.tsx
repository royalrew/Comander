"use client";

import React, { useEffect, useMemo, useState } from 'react';
import { Database, Search, History, Trash2, ShieldAlert, Sparkles, Filter, RefreshCw } from 'lucide-react';

export default function MemoryPage() {
    const [memories, setMemories] = useState<any[]>([]);
    const [status, setStatus] = useState<any>(null);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [query, setQuery] = useState("");
    const [categoryFilter, setCategoryFilter] = useState<string>("all");

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

    // Calculate memory percentage safely (Postgres-backed vectors)
    let memoryUsageStr = status?.memory_usage || "0/10000 vectors";
    let memoryCount = parseInt(memoryUsageStr.split("/")[0]) || 0;
    let maxMemory = parseInt(memoryUsageStr.split("/")[1]) || 10000;
    let memoryPercent = Math.min((memoryCount / maxMemory) * 100, 100);

    // Unique categories for filter pills
    const categories = useMemo(
        () => Array.from(new Set(memories.map((m) => m.category || "General"))),
        [memories]
    );

    // Local in-memory filtering & search (no OpenSearch)
    const filteredMemories = useMemo(() => {
        return memories.filter((mem) => {
            const matchesCategory =
                categoryFilter === "all" || (mem.category || "General") === categoryFilter;
            const matchesQuery =
                !query.trim() ||
                mem.text?.toLowerCase().includes(query.toLowerCase()) ||
                mem.category?.toLowerCase().includes(query.toLowerCase());
            return matchesCategory && matchesQuery;
        });
    }, [memories, categoryFilter, query]);

    return (
        <div className="space-y-8 animate-fade-in">
            <header className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight steel-text flex items-center gap-3">
                        <Database className="text-blue-500" size={32} />
                        Minne & Konvergens
                    </h1>
                    <p className="mt-2 text-muted-foreground">
                        Långtidsminne och semantisk kontext, nu helt migrerat till PostgreSQL‑baserade vektorer.
                    </p>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={fetchData}
                        disabled={isRefreshing}
                        className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-xl border border-white/10 transition-colors text-sm font-medium disabled:opacity-50"
                    >
                        {isRefreshing ? (
                            <RefreshCw size={16} className="text-blue-400 animate-spin" />
                        ) : (
                            <History size={16} className="text-blue-400" />
                        )}
                        {isRefreshing ? 'Uppdaterar...' : 'Synka nu'}
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-xl border border-red-500/30 transition-colors text-sm font-medium">
                        <Trash2 size={16} />
                        Glömskestorm (snart)
                    </button>
                </div>
            </header>

            {/* Search & Filters */}
            <div className="mb-8 flex flex-col lg:flex-row gap-4 items-stretch lg:items-center justify-between">
                <div className="relative flex-1">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Search className="text-muted-foreground" size={20} />
                    </div>
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Sök i AI:ns minne (lokal vektor‑sök, ingen OpenSearch)..."
                        className="w-full bg-black/40 border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-white outline-none focus:border-blue-500/50 shadow-[inset_0_2px_10px_rgba(0,0,0,0.5)] transition-all"
                    />
                </div>
                <div className="flex flex-wrap gap-2 lg:justify-end">
                    <button
                        onClick={() => setCategoryFilter("all")}
                        className={`inline-flex items-center gap-2 px-3 py-2 rounded-2xl text-xs font-mono tracking-widest uppercase border transition-all ${
                            categoryFilter === "all"
                                ? "bg-blue-500/20 border-blue-500/60 text-blue-300"
                                : "bg-white/5 border-white/10 text-muted-foreground hover:bg-white/10"
                        }`}
                    >
                        <Filter size={14} />
                        Alla
                    </button>
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => setCategoryFilter(cat)}
                            className={`inline-flex items-center gap-2 px-3 py-2 rounded-2xl text-xs font-mono tracking-widest uppercase border transition-all ${
                                categoryFilter === cat
                                    ? "bg-emerald-500/20 border-emerald-500/60 text-emerald-300"
                                    : "bg-white/5 border-white/10 text-muted-foreground hover:bg-white/10"
                            }`}
                        >
                            <Sparkles size={14} />
                            {cat}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* RAG Database State */}
                <div className="lg:col-span-2 space-y-6">
                    <h2 className="text-xl font-bold steel-text flex items-center gap-2">
                        <History className="text-blue-400" size={20} />
                        Senaste Inlärning (Vektor‑minne)
                    </h2>

                    <div className="glass rounded-3xl border border-white/5 overflow-hidden">
                        <div className="max-h-[480px] overflow-y-auto custom-scrollbar divide-y divide-white/5 text-gray-300">
                            {filteredMemories.map((mem, i) => (
                                <div
                                    key={i}
                                    className="px-6 py-4 hover:bg-white/5 transition-colors group flex flex-col gap-2"
                                >
                                    <div className="flex items-center justify-between gap-3">
                                        <span className="text-[10px] font-mono text-blue-200 bg-blue-500/10 border border-blue-500/30 px-2 py-0.5 rounded-full uppercase tracking-widest">
                                            {mem.category || "General"}
                                        </span>
                                        <span className="text-muted-foreground text-[11px] whitespace-nowrap">
                                            {mem.timestamp
                                                ? new Date(mem.timestamp).toLocaleString("sv-SE", {
                                                      dateStyle: "short",
                                                      timeStyle: "short",
                                                  })
                                                : "Okänt"}
                                        </span>
                                    </div>
                                    <p className="font-mono text-xs text-blue-100 leading-relaxed whitespace-pre-wrap">
                                        {mem.text}
                                    </p>
                                </div>
                            ))}
                            {filteredMemories.length === 0 && (
                                <div className="px-6 py-12 text-center text-muted-foreground text-sm">
                                    {memories.length === 0
                                        ? status
                                            ? "Hittade inga sparade vektorer i minnesbanken ännu."
                                            : "Laddar minnen från vektor‑minnet..."
                                        : "Inga minnen matchar den här filtreringen/sökningen."}
                                </div>
                            )}
                        </div>
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
                                <span>Vektor‑minne (PostgreSQL)</span>
                                <span className={memoryPercent > 80 ? "text-red-400" : "text-emerald-400"}>
                                    {memoryPercent.toFixed(1)}%
                                </span>
                            </div>
                            <div className="w-full h-2 rounded-full bg-black/50 overflow-hidden border border-white/5">
                                <div
                                    className={`h-full ${
                                        memoryPercent > 80
                                            ? 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]'
                                            : 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]'
                                    } rounded-full transition-all duration-1000`}
                                    style={{ width: `${memoryPercent}%` }}
                                ></div>
                            </div>
                            <p className="text-[10px] text-muted-foreground mt-2">
                                {memoryCount} vektorminnen indexerade (Max {maxMemory})
                            </p>
                        </div>

                        <div className="pt-4 border-t border-white/10">
                            <div className="flex justify-between text-xs font-bold text-muted-foreground tracking-widest uppercase mb-2">
                                <span>Cortex & Sessions</span>
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
