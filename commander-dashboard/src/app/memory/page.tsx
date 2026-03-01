import React from 'react';
import { Database, Search, History, Trash2, ShieldAlert } from 'lucide-react';

export default function MemoryPage() {
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
                                    <th className="px-6 py-4 font-bold">Dokument / Källa</th>
                                    <th className="px-6 py-4 font-bold">Kategori</th>
                                    <th className="px-6 py-4 font-bold">Tokens</th>
                                    <th className="px-6 py-4 font-bold text-right">Tidpunkt</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5 text-gray-300">
                                <tr className="hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4 font-mono text-blue-400">master.prompt.md</td>
                                    <td className="px-6 py-4"><span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded-md text-[10px] uppercase font-bold tracking-wider">System Regler</span></td>
                                    <td className="px-6 py-4">4,520</td>
                                    <td className="px-6 py-4 text-right text-muted-foreground">Idag 14:32</td>
                                </tr>
                                <tr className="hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4 font-mono text-blue-400">api_test_results.json</td>
                                    <td className="px-6 py-4"><span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded-md text-[10px] uppercase font-bold tracking-wider">Verifiering</span></td>
                                    <td className="px-6 py-4">842</td>
                                    <td className="px-6 py-4 text-right text-muted-foreground">Idag 10:15</td>
                                </tr>
                                <tr className="hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4 font-mono text-blue-400">ceo_profile.yaml</td>
                                    <td className="px-6 py-4"><span className="px-2 py-1 bg-amber-500/20 text-amber-400 rounded-md text-[10px] uppercase font-bold tracking-wider">Kontext</span></td>
                                    <td className="px-6 py-4">120</td>
                                    <td className="px-6 py-4 text-right text-muted-foreground">Igår</td>
                                </tr>
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
                                <span className="text-emerald-400">12%</span>
                            </div>
                            <div className="w-full h-2 rounded-full bg-black/50 overflow-hidden border border-white/5">
                                <div className="h-full bg-emerald-500 rounded-full w-[12%] shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                            </div>
                            <p className="text-[10px] text-muted-foreground mt-2">124 dokument indexerade (Max 1000)</p>
                        </div>

                        <div className="pt-4 border-t border-white/10">
                            <div className="flex justify-between text-xs font-bold text-muted-foreground tracking-widest uppercase mb-2">
                                <span>Postgres Sessions</span>
                                <span className="text-blue-400">4 Active</span>
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
