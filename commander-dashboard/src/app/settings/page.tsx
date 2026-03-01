import React from 'react';
import { Settings2, Clock, DollarSign, Cpu, AlertTriangle, Save, ShieldCheck, Lock } from 'lucide-react';

export default function SettingsPage() {
    return (
        <div className="space-y-8 animate-fade-in">
            <header className="mb-10">
                <h1 className="text-3xl font-bold tracking-tight steel-text flex items-center gap-3">
                    <Settings2 className="text-primary" size={32} />
                    Inställningar
                </h1>
                <p className="mt-2 text-muted-foreground">
                    Kärnkonfiguration för The Commander, CFO-gränser och Heartbeat.
                </p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Heartbeat Settings */}
                <div className="p-8 glass rounded-3xl border border-white/5 space-y-6">
                    <div className="flex items-center gap-3 pb-4 border-b border-white/10">
                        <Clock className="text-purple-500" />
                        <h2 className="text-xl font-bold">The Watchdog (Heartbeat)</h2>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs font-bold text-muted-foreground tracking-widest uppercase mb-2">
                                Pulsintervall
                            </label>
                            <select className="w-full bg-black/40 border border-white/10 rounded-xl p-3 text-sm text-gray-200 outline-none focus:border-purple-500/50 appearance-none">
                                <option value="15">Var 15:e minut (Aggressiv)</option>
                                <option value="60">Varje timme (Standard)</option>
                                <option value="360">Var 6:e timme (Bevarande)</option>
                                <option value="1440">En gång per dygn (Endast Morning Briefing)</option>
                            </select>
                            <p className="text-[10px] text-muted-foreground mt-2 leading-relaxed">
                                Hur ofta den lokala Llama 3 vaktar-agenten ska vakna och skanna filsystemet gratis.
                            </p>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-muted-foreground tracking-widest uppercase mb-2 mt-4">
                                Watchdog Trigger Känslighet
                            </label>
                            <input type="range" min="1" max="10" defaultValue="5" className="w-full accent-purple-500" />
                            <div className="flex justify-between text-[10px] text-muted-foreground mt-1">
                                <span>Väcker sällan Cortex</span>
                                <span>Väcker för minsta lilla</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* CFO Circuit Breaker */}
                <div className="p-8 glass rounded-3xl border border-white/5 space-y-6">
                    <div className="flex items-center gap-3 pb-4 border-b border-white/10">
                        <DollarSign className="text-emerald-500" />
                        <h2 className="text-xl font-bold">CFO Circuit Breaker</h2>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs font-bold text-muted-foreground tracking-widest uppercase mb-2">
                                Maximal Daglig Budget (USD)
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <span className="text-muted-foreground font-bold">$</span>
                                </div>
                                <input
                                    type="number"
                                    defaultValue="2.00"
                                    step="0.50"
                                    className="w-full bg-black/40 border border-white/10 rounded-xl py-3 pl-8 pr-3 text-sm text-emerald-400 font-bold outline-none focus:border-emerald-500/50"
                                />
                            </div>
                            <p className="text-[10px] text-has-warning mt-2 leading-relaxed text-amber-500/80">
                                <AlertTriangle className="inline w-3 h-3 mr-1" />
                                Om AI:n överskrider denna budget bryts strömmen ("nödstopp") och en varning skickas i Telegram.
                            </p>
                        </div>
                    </div>
                </div>

                {/* System Models Configuration */}
                <div className="p-8 glass rounded-3xl border border-white/5 space-y-6 lg:col-span-2">
                    <div className="flex items-center gap-3 pb-4 border-b border-white/10">
                        <Cpu className="text-blue-500" />
                        <h2 className="text-xl font-bold">Agentisk Hierarki (LLMs)</h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="space-y-2">
                            <label className="block text-[10px] font-bold text-muted-foreground tracking-widest uppercase mb-2">
                                The Cortex (Arkitekten)
                            </label>
                            <select className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-sm text-gray-200 outline-none focus:border-blue-500/50">
                                <option value="gpt-4o">GPT-4o (OpenAI)</option>
                                <option value="claude-3-opus">Claude 3 Opus (Anthropic)</option>
                            </select>
                        </div>

                        <div className="space-y-2">
                            <label className="block text-[10px] font-bold text-muted-foreground tracking-widest uppercase mb-2">
                                Muscle Coder (Utövaren)
                            </label>
                            <select className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-sm text-gray-200 outline-none focus:border-blue-500/50">
                                <option value="deepseek-coder">DeepSeek Coder V2</option>
                                <option value="minimax">MiniMax/ABAB6.5</option>
                                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                            </select>
                        </div>

                        <div className="space-y-2">
                            <label className="block text-[10px] font-bold text-muted-foreground tracking-widest uppercase mb-2">
                                The Watchdog (Övervakaren)
                            </label>
                            <select className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-sm text-gray-200 outline-none focus:border-blue-500/50">
                                <option value="ollama/llama3">Llama 3 (Lokal Olamma)</option>
                                <option value="ollama/phi3">Phi-3 (Lokal Ollama)</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* --- NY GRC FUNKTIONALITET (The Canary Critique) --- */}

                {/* Data Privacy & Compliance */}
                <div className="p-8 glass rounded-3xl border border-white/5 space-y-6">
                    <div className="flex items-center gap-3 pb-4 border-b border-white/10">
                        <ShieldCheck className="text-emerald-500" />
                        <h2 className="text-xl font-bold">Data Sovereignty (PII)</h2>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 rounded-xl bg-black/40 border border-white/5">
                            <div>
                                <span className="text-sm font-bold text-white block">Auto-Maskera PII Data</span>
                                <span className="text-[10px] text-muted-foreground mt-1">Använder Microsoft Presidio före alla GPT-4o anrop.</span>
                            </div>
                            <div className="w-10 h-5 rounded-full relative cursor-pointer transition-colors bg-emerald-500">
                                <div className="absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all left-[22px]" />
                            </div>
                        </div>

                        <div className="flex items-center justify-between p-4 rounded-xl bg-black/40 border border-white/5">
                            <div>
                                <span className="text-sm font-bold text-white block">GDPR Expungement Policy</span>
                                <span className="text-[10px] text-muted-foreground mt-1">Radera autologgar äldre än 30 dagar från databasen.</span>
                            </div>
                            <div className="w-10 h-5 rounded-full relative cursor-pointer transition-colors bg-secondary">
                                <div className="absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all left-0.5" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Human-in-the-Loop Approvals & Vault */}
                <div className="p-8 glass rounded-3xl border border-white/5 space-y-6">
                    <div className="flex items-center gap-3 pb-4 border-b border-white/10">
                        <Lock className="text-amber-500" />
                        <h2 className="text-xl font-bold">Autonomy Thresholds & Vault</h2>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs font-bold text-muted-foreground tracking-widest uppercase mb-2">
                                Telegram Manual Approval Mappar
                            </label>
                            <input
                                type="text"
                                defaultValue="db/, payments/, auth/"
                                className="w-full bg-black/40 border border-amber-500/20 rounded-xl p-3 text-sm text-amber-500 outline-none focus:border-amber-500/50"
                            />
                            <p className="text-[10px] text-muted-foreground mt-2 leading-relaxed">
                                Om `surgeon.py` försöker redigera filer i dessa mappar, SKALL den pausa The ReAct Loop och vänta på ditt "GO!" i Telegram.
                            </p>
                        </div>

                        <div className="pt-4 mt-4 border-t border-white/5">
                            <label className="block text-[10px] font-bold text-muted-foreground tracking-widest uppercase mb-2">
                                Stripe Secret Key (Encrypted Vault)
                            </label>
                            <div className="flex gap-2">
                                <input
                                    type="password"
                                    defaultValue="sk_live_1234567890abcdef"
                                    className="flex-1 bg-black/40 border border-white/10 rounded-lg p-2.5 text-sm text-gray-200 outline-none focus:border-primary/50"
                                />
                                <button className="px-3 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 transition-colors">
                                    <span className="text-xs">Update</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

            <div className="flex justify-end pt-6">
                <button className="flex items-center gap-2 px-8 py-3 bg-primary hover:bg-primary/80 text-primary-foreground font-bold text-sm tracking-widest uppercase rounded-xl transition-all shadow-[0_0_20px_rgba(var(--primary),0.3)] hover:shadow-[0_0_30px_rgba(var(--primary),0.5)]">
                    <Save size={16} />
                    Spara Parametrar
                </button>
            </div>
        </div>
    );
}
