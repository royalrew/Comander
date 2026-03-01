import React from 'react';
import { Wrench, Globe, Terminal, Code, Power, AlertCircle } from 'lucide-react';

export const dynamic = 'force-dynamic';

async function getToolsStatus() {
    try {
        // Fetching from the new commander-core FastAPI server
        const res = await fetch('http://127.0.0.1:8000/api/v1/tools/status', {
            cache: 'no-store',
            next: { revalidate: 0 }
        });
        if (!res.ok) throw new Error('API down');
        return res.json();
    } catch (e) {
        return null;
    }
}

export default async function ToolsPage() {
    const data = await getToolsStatus();

    // Fallback defaults if backend is offline
    const isObserverActive = data?.tools?.find((t: any) => t.id === 'file_observer')?.active ?? false;
    const isSurgeonActive = data?.tools?.find((t: any) => t.id === 'the_surgeon')?.active ?? false;
    const isScraperActive = data?.tools?.find((t: any) => t.id === 'omni_scraper')?.active ?? false;

    const allowedDomainsText = data?.allowed_domains?.join('\n') ?? "https://docs.microsoft.com/*\nhttps://stripe.com/docs/*\nhttps://nextjs.org/docs/*";

    return (
        <div className="space-y-8 animate-fade-in">
            <header className="mb-10">
                <h1 className="text-3xl font-bold tracking-tight steel-text flex items-center gap-3">
                    <Wrench className="text-amber-500" size={32} />
                    Verktyg & Arsenal Control
                </h1>
                <p className="mt-2 text-muted-foreground flex items-center gap-2">
                    Styr vilka verktyg (Function Calling) som The Cortex har tillgång till i The ReAct Loop.
                    {!data && <span className="text-xs text-red-400 bg-red-400/10 px-2 py-0.5 rounded border border-red-400/20 flex items-center gap-1"><AlertCircle size={12} /> API Offline</span>}
                </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">

                {/* Tool: File Observer */}
                <div className={`p-6 glass rounded-3xl border flex flex-col transition-all duration-500 ${isObserverActive ? 'border-white/5 opacity-100' : 'border-white/5 opacity-50 grayscale hover:grayscale-0'}`}>
                    <div className="flex items-start justify-between mb-4">
                        <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                            <Terminal className="text-blue-400" size={24} />
                        </div>
                        <div className={`w-12 h-6 rounded-full relative cursor-pointer transition-colors ${isObserverActive ? 'bg-emerald-500 border border-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.3)]' : 'bg-zinc-800 border border-zinc-700'}`}>
                            <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-all ${isObserverActive ? 'left-[22px]' : 'left-0.5 bg-zinc-500'}`} />
                        </div>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">File Observer</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                        Låter agenten lista mappar, läsa filer (`read_file`) och söka igenom kodbasen. Endast läsrättigheter (Read-Only).
                    </p>
                    <div className="mt-4 pt-4 border-t border-white/5 flex justify-between items-center text-[10px] tracking-widest text-muted-foreground uppercase font-bold">
                        <span>Modul: observer.py</span>
                        <span className={isObserverActive ? "text-emerald-400" : "text-gray-500"}>{isObserverActive ? "Aktiv" : "Inaktiv"}</span>
                    </div>
                </div>

                {/* Tool: The Surgeon */}
                <div className={`p-6 glass rounded-3xl flex flex-col relative overflow-hidden group transition-all duration-500 ${isSurgeonActive ? 'border border-amber-500/20 opacity-100' : 'border border-white/5 opacity-50 grayscale hover:grayscale-0'}`}>
                    {isSurgeonActive && <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent pointer-events-none" />}
                    <div className="flex items-start justify-between mb-4 relative z-10">
                        <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center">
                            <Code className="text-amber-400" size={24} />
                        </div>
                        <div className={`w-12 h-6 rounded-full relative cursor-pointer transition-colors ${isSurgeonActive ? 'bg-emerald-500 border border-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.3)]' : 'bg-zinc-800 border border-zinc-700'}`}>
                            <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-all ${isSurgeonActive ? 'left-[22px]' : 'left-0.5 bg-zinc-500'}`} />
                        </div>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2 relative z-10 flex items-center gap-2">
                        The Surgeon
                        <span className="px-2 py-0.5 rounded text-[10px] bg-red-500/20 text-red-400 uppercase tracking-widest">Kritiskt</span>
                    </h3>
                    <p className="text-sm text-muted-foreground leading-relaxed flex-1 relative z-10">
                        Skrivrättigheter. Låter agenten skriva ny kod, refaktorera existerande kod (`refactor_file`) och bygga projekt. Begränsad av Zero-Trust Jail.
                    </p>
                    <div className="mt-4 pt-4 border-t border-white/5 flex justify-between items-center text-[10px] tracking-widest text-muted-foreground uppercase font-bold relative z-10">
                        <span>Modul: surgeon.py</span>
                        <span className={isSurgeonActive ? "text-emerald-400" : "text-gray-500"}>{isSurgeonActive ? "Aktiv" : "Inaktiv"}</span>
                    </div>
                </div>

                {/* Tool: Web Scraper */}
                <div className={`p-6 glass rounded-3xl flex flex-col transition-all duration-500 ${isScraperActive ? 'border border-purple-500/20 opacity-100' : 'border border-white/5 opacity-60 grayscale hover:grayscale-0'}`}>
                    <div className="flex items-start justify-between mb-4">
                        <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                            <Globe className="text-purple-400" size={24} />
                        </div>
                        <div className={`w-12 h-6 rounded-full relative cursor-pointer transition-colors ${isScraperActive ? 'bg-emerald-500 border border-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.3)]' : 'bg-zinc-800 border border-zinc-700'}`}>
                            <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-all ${isScraperActive ? 'left-[22px]' : 'left-0.5 bg-zinc-500'}`} />
                        </div>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">Omni-Scraper</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                        Access till öppna internet. Kan besöka URLs, ladda ner information och mata det till RAG:en. Kräver godkänd Whitelist nedan.
                    </p>
                    <div className="mt-4 pt-4 border-t border-white/5 flex justify-between items-center text-[10px] tracking-widest text-muted-foreground uppercase font-bold">
                        <span>Modul: scraper.py</span>
                        <span className={isScraperActive ? "text-emerald-400" : "text-gray-500"}>{isScraperActive ? "Aktiv" : "Inaktiv"}</span>
                    </div>
                </div>

            </div>

            {/* Scraping Whitelist Settings */}
            <div className="mt-10 p-8 glass rounded-3xl border border-white/5 space-y-6">
                <div>
                    <h2 className="text-xl font-bold steel-text mb-2">Scraping Whitelist (Allowed Domains)</h2>
                    <p className="text-sm text-muted-foreground">Vilka specifika externa siter får webb-skrapan besöka? Detta förhindrar att AI:n oavsiktligt hämtar kod eller data från opålitliga källor.</p>
                </div>

                <div className="space-y-4">
                    <textarea
                        className="w-full h-32 bg-black/40 border border-white/10 rounded-xl p-4 text-sm text-blue-400 font-mono outline-none focus:border-blue-500/50 resize-none"
                        defaultValue={allowedDomainsText}
                    />
                    <div className="flex justify-end">
                        <button className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white font-bold text-xs tracking-widest uppercase rounded-lg transition-all">
                            Uppdatera Whitelist
                        </button>
                    </div>
                </div>
            </div>

        </div>
    );
}
