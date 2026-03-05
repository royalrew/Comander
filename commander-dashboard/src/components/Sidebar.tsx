import React from 'react';
import Link from 'next/link';
import {
    Home,
    Database,
    Wrench,
    Target,
    Settings,
    PowerOff,
    DollarSign,
    HeartPulse,
    Activity,
    Cpu,
    Calendar,
    Sparkles,
} from 'lucide-react';

export default function Sidebar() {
    const navItems = [
        { name: 'Översikt', icon: Home, href: '/' },
        { name: 'Teknisk Agent', icon: Cpu, href: '/agents/tech' },
        { name: 'Hälsoagent', icon: HeartPulse, href: '/agents/health' },
        { name: 'Finansagent', icon: DollarSign, href: '/agents/finance' },
        { name: 'Minne & Konvergens', icon: Database, href: '/memory' },
        { name: 'Kalender', icon: Calendar, href: '/calendar' },
        { name: 'Verktyg & Arsenal', icon: Wrench, href: '/tools' },
        { name: 'Mål & Planer', icon: Target, href: '/plans' },
        { name: 'Hype Engine', icon: Sparkles, href: '/hype-engine' },
        { name: 'Inställningar', icon: Settings, href: '/settings' },
    ];

    return (
        <div className="w-64 h-full glass border-r border-white/5 flex flex-col pt-8 pb-6 px-4 shrink-0 shadow-[4px_0_24px_-4px_rgba(0,0,0,0.5)] z-50">

            {/* Brand */}
            <div className="flex items-center gap-3 px-2 mb-10">
                <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
                    <Cpu className="text-primary w-5 h-5" />
                </div>
                <div>
                    <h2 className="text-lg font-bold steel-text tracking-wide leading-tight">SINTARI</h2>
                    <p className="text-[10px] text-primary uppercase tracking-widest font-mono font-bold">Commander OS</p>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1">
                {navItems.map((item) => (
                    <Link
                        key={item.name}
                        href={item.href}
                        className={`flex items-center gap-3 px-3 py-3 rounded-xl transition-all w-full text-sm font-medium ${item.name === 'Översikt'
                            ? 'bg-primary/10 text-primary border border-primary/20 shadow-[inset_0_0_12px_rgba(var(--primary),0.2)]'
                            : 'text-muted-foreground hover:bg-white/5 hover:text-white'
                            }`}
                    >
                        <item.icon className={`w-4 h-4 ${item.name === 'Översikt' ? 'opacity-100' : 'opacity-70'}`} />
                        {item.name}
                    </Link>
                ))}
            </nav>

            {/* System Status */}
            <div className="mb-6 px-4 py-3 rounded-xl bg-black/40 border border-white/5">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold">Nätverk</span>
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-pulse" />
                </div>
                <p className="text-xs text-gray-300 font-mono">WS: Ansluten</p>
                <p className="text-xs text-gray-400 font-mono mt-1">Svarstid: 12ms</p>
            </div>

            {/* Kill Switch */}
            <button className="flex items-center justify-center gap-2 w-full py-3 px-4 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-500 font-bold text-sm tracking-wider uppercase transition-all border border-red-500/20 hover:border-red-500/50 shadow-[0_0_15px_-3px_rgba(239,68,68,0.2)] group hover:shadow-[0_0_20px_0_rgba(239,68,68,0.4)]">
                <PowerOff className="w-4 h-4 group-hover:scale-110 transition-transform" />
                Nödstopp
            </button>

        </div>
    );
}
