"use client";

import React, { useEffect, useState } from 'react';
import { Cpu, Terminal, Database, Activity } from 'lucide-react';

export default function CortexMonitor() {
    const [status, setStatus] = useState<any>(null);
    const [logs, setLogs] = useState<any[]>([]);
    const [memories, setMemories] = useState<any[]>([]);
    const [isOnline, setIsOnline] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://comander-production.up.railway.app';
            try {
                const [statusRes, logsRes, memRes] = await Promise.all([
                    fetch(`${API_URL}/api/v1/cortex/status`),
                    fetch(`${API_URL}/api/v1/cortex/logs`),
                    fetch(`${API_URL}/api/v1/cortex/memories`)
                ]);

                if (statusRes.ok) {
                    setStatus(await statusRes.json());
                    setIsOnline(true);
                } else setIsOnline(false);

                if (logsRes.ok) setLogs((await logsRes.json()).logs || []);
                if (memRes.ok) setMemories((await memRes.json()).memories || []);
            } catch (err) {
                setIsOnline(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-8 glass rounded-3xl border border-white/5 flex flex-col gap-6 h-full col-span-1 lg:col-span-2">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-xl font-bold flex items-center gap-3 text-white">
                        <Cpu className="text-blue-500" />
                        The Cortex Monitor
                    </h2>
                    <p className="text-xs text-muted-foreground mt-1">Live Telemetry & Semantic Memory</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="text-[10px] font-mono font-bold text-zinc-400 bg-black/40 px-2 py-1 rounded border border-white/10 uppercase tracking-widest hidden md:block">
                        {status?.memory_usage || 'Loading vectors...'}
                    </div>
                    <div className="text-[10px] font-mono font-bold text-blue-400 bg-blue-500/10 px-2 py-1 rounded border border-blue-500/20 uppercase tracking-widest hidden md:block">
                        {status?.active_model || 'Connecting...'}
                    </div>
                    <span className="relative flex h-3 w-3">
                        {isOnline && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
                        <span className={`relative inline-flex rounded-full h-3 w-3 ${isOnline ? 'bg-emerald-500 shadow-[0_0_8px_theme(colors.emerald.500)]' : 'bg-red-500'}`}></span>
                    </span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
                {/* Memory Feed */}
                <div className="flex flex-col gap-3">
                    <h3 className="text-xs font-bold text-blue-400 uppercase tracking-widest flex items-center gap-2">
                        <Database size={14} /> Active Memory (OpenSearch)
                    </h3>
                    <div className="flex-1 p-4 rounded-2xl bg-black/40 border border-white/5 overflow-y-auto max-h-[300px] space-y-3">
                        {memories.map((mem, i) => (
                            <div key={i} className="flex flex-col gap-1 p-3 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                                <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-mono text-blue-400 px-1.5 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">{mem.category || 'General'}</span>
                                    <span className="text-zinc-500 text-[10px]">{new Date(mem.timestamp).toLocaleTimeString()}</span>
                                </div>
                                <p className="text-sm text-zinc-300 leading-snug line-clamp-3 mt-1.5" title={mem.text}>{mem.text}</p>
                            </div>
                        ))}
                        {memories.length === 0 && <div className="text-xs text-muted-foreground py-8 text-center">Inga nyliga vektorer laddade...</div>}
                    </div>
                </div>

                {/* System Console Logs */}
                <div className="flex flex-col gap-3">
                    <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-2">
                        <Terminal size={14} /> System Console (PostgreSQL)
                    </h3>
                    <div className="flex-1 p-4 rounded-2xl bg-[#0a0a0a] border border-white/5 overflow-y-auto max-h-[300px] space-y-2 font-mono">
                        {logs.map((log, i) => (
                            <div key={i} className="flex gap-3 text-[11px] border-b border-white/5 pb-2 last:border-0 hover:bg-white/5 p-1 rounded transition-colors">
                                <span className="text-zinc-600 shrink-0">{new Date(log.timestamp).toLocaleTimeString()}</span>
                                <span className="text-emerald-400 shrink-0 min-w-[100px] max-w-[120px] truncate" title={log.action}>[{log.action}]</span>
                                <span className="text-zinc-300 break-words">{log.details}</span>
                            </div>
                        ))}
                        {logs.length === 0 && <div className="text-[11px] text-zinc-600">Waiting for system logs...</div>}
                    </div>
                </div>
            </div>
        </div>
    );
}
