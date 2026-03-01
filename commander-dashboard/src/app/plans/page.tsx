import React from 'react';
import { Target, Calendar, Plus, Rocket, Play, Pause } from 'lucide-react';

export default function PlansPage() {
    return (
        <div className="space-y-8 animate-fade-in">
            <header className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight steel-text flex items-center gap-3">
                        <Target className="text-red-500" size={32} />
                        Watchdog Planner & Mål
                    </h1>
                    <p className="mt-2 text-muted-foreground">
                        Planera proaktiva uppdrag ("Missions") som Llama 3 och The Cortex ska utföra asynkront.
                    </p>
                </div>

                <button className="flex items-center justify-center gap-2 px-6 py-3 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-xl border border-red-500/30 transition-all font-bold tracking-widest uppercase text-sm shadow-[0_0_15px_-3px_rgba(239,68,68,0.2)]">
                    <Rocket size={18} />
                    Injecera Override (Mål)
                </button>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Active Missions */}
                <div className="p-8 glass rounded-3xl border border-white/5 space-y-6">
                    <div className="flex items-center justify-between pb-4 border-b border-white/10">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <Play className="text-emerald-500" size={20} />
                            Aktiva Cykler
                        </h2>
                        <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 rounded-full text-xs font-bold tracking-widest uppercase">
                            2 Running
                        </span>
                    </div>

                    <div className="space-y-4">
                        {/* Mission 1 */}
                        <div className="p-4 rounded-2xl bg-black/40 border border-white/5">
                            <div className="flex justify-between items-start mb-2">
                                <h3 className="font-bold text-white">Morning Briefing Generator</h3>
                                <span className="text-[10px] px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded uppercase font-bold tracking-wider">07:00</span>
                            </div>
                            <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                                Sammanställer en rapport över nattens loggar, server-status och CFO spend, och skickar till VD:n på Telegram.
                            </p>
                            <div className="flex items-center gap-4 text-[10px] font-mono text-gray-400">
                                <span>Nästa: om 11h 20m</span>
                                <div className="flex-1 h-1 bg-black rounded-full overflow-hidden">
                                    <div className="h-full bg-emerald-500 w-[10%]"></div>
                                </div>
                            </div>
                        </div>

                        {/* Mission 2 */}
                        <div className="p-4 rounded-2xl bg-black/40 border border-emerald-500/20 shadow-[inset_0_0_20px_rgba(16,185,129,0.05)]">
                            <div className="flex justify-between items-start mb-2">
                                <h3 className="font-bold text-emerald-400">The Hype Engine (Phase 2)</h3>
                                <span className="text-[10px] px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded uppercase font-bold tracking-wider">Timvis</span>
                            </div>
                            <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                                Genererar assets och förbereder social media drops. Väntar just nu på ny kontext från R2 bucketen.
                            </p>
                            <div className="flex items-center gap-4 text-[10px] font-mono text-gray-400">
                                <span className="flex items-center gap-1 text-emerald-400"><span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> Körs Nu</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Planned / Paused Missions */}
                <div className="p-8 glass rounded-3xl border border-white/5 space-y-6">
                    <div className="flex items-center justify-between pb-4 border-b border-white/10">
                        <h2 className="text-xl font-bold flex items-center gap-2 text-muted-foreground">
                            <Pause size={20} />
                            Vilande / Planerade
                        </h2>
                        <button className="flex items-center justify-center w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 text-white transition-colors">
                            <Plus size={16} />
                        </button>
                    </div>

                    <div className="space-y-4">
                        {/* Mission 3 */}
                        <div className="p-4 rounded-2xl bg-black/40 border border-white/5 opacity-60">
                            <div className="flex justify-between items-start mb-2">
                                <h3 className="font-bold text-white">Stripe Faktura Sync (Phase 4)</h3>
                                <span className="text-[10px] px-2 py-0.5 bg-gray-500/20 text-gray-400 rounded uppercase font-bold tracking-wider">Paused</span>
                            </div>
                            <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                                Synkroniserar abonnemang med PostgreSQL databasen. Inväntar uppsättning av Stripe Webhooks.
                            </p>
                            <div className="flex gap-2">
                                <button className="px-3 py-1.5 bg-white/5 hover:bg-white/10 rounded-lg text-[10px] font-bold tracking-widest uppercase transition-colors">Aktivera</button>
                                <button className="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-lg text-[10px] font-bold tracking-widest uppercase transition-colors">Radera</button>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
