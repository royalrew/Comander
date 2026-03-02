import React from 'react';
import {
  Activity,
  ShieldCheck,
  Zap,
  TrendingUp,
  Cpu,
  AlertCircle,
  Lock,
  Database,
  Globe,
  DollarSign
} from 'lucide-react';
import CortexMonitor from '@/components/CortexMonitor';
import FinanceCard from '@/components/FinanceCard';

async function getCfoStatus() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://comander-production.up.railway.app';
  try {
    const res = await fetch(`${API_URL}/api/v1/cfo/status`, {
      cache: 'no-store',
      next: { revalidate: 0 }
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function DashboardPage() {
  const cfoData = await getCfoStatus();
  const spend = cfoData?.daily_spend !== undefined ? cfoData.daily_spend.toFixed(2) : '0.00';
  const limit = cfoData?.daily_limit !== undefined ? cfoData.daily_limit.toFixed(2) : '5.00';
  const spendPercentage = cfoData ? Math.min((cfoData.daily_spend / cfoData.daily_limit) * 100, 100) : 0;

  return (
    <div className="space-y-10">
      {/* Header Section */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight steel-text">
            The Commander
          </h1>
          <p className="mt-2 text-muted-foreground">
            Enterprise GRC Autonom Agent — Genesis Protokoll Aktivt
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-emerald-400 border rounded-full glass border-emerald-500/20 bg-emerald-500/10">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Kärnstatus: Optimal
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-blue-400 border rounded-full glass border-blue-500/20 bg-blue-500/10">
            <ShieldCheck size={14} />
            Noll-Hallucination Kritiker Aktiv
          </div>
        </div>
      </header>

      {/* Main Vision Banner */}
      <div className="relative overflow-hidden p-8 glass rounded-3xl border border-white/5">
        <div className="absolute top-0 right-0 p-8 opacity-10">
          <TrendingUp size={120} className="text-blue-500" />
        </div>
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-2 py-1 mb-4 text-[10px] font-bold tracking-widest uppercase rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
            Genesis Uppdrag
          </div>
          <h2 className="text-3xl font-semibold mb-4 text-white">
            "Automatisering ger fokus. Fokus ger frihet."
          </h2>
          <p className="text-muted-foreground leading-relaxed">
            Commandern orkestrerar för närvarande The Hype Engine.
            Alla deterministiska övervakare är aktiva och kontrollerar kodintegritet samt finansiella buffertar.
          </p>
        </div>
      </div>

      {/* Phase 5 Command Center Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* The Cortex Monitor */}
        <CortexMonitor />

        {/* Right Column: Finance, Arsenal, Watchdog */}
        <div className="flex flex-col gap-8 col-span-1">
          <FinanceCard initialData={cfoData} />

          {/* Arsenal Control */}
          <div className="p-8 glass rounded-3xl border border-white/5 flex flex-col gap-6">
            <h2 className="text-xl font-bold flex items-center gap-3">
              <Lock className="text-amber-500" />
              Arsenal Control
            </h2>

            <div className="space-y-4">
              <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Aktivt Verktygsbälte</h3>
              {[
                { name: 'refactor_file (Surgeon)', active: true },
                { name: 'list_files (IO Jail)', active: true },
                { name: 'web_scraper (Selenium)', active: false },
                { name: 'database_query (Neo4j)', active: false }
              ].map((tool, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5">
                  <span className="text-sm font-medium">{tool.name}</span>
                  <div className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${tool.active ? 'bg-primary' : 'bg-secondary'}`}>
                    <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${tool.active ? 'left-[22px]' : 'left-0.5'}`} />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-auto">
              <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-2">Scraping Whitelist</h3>
              <textarea
                className="w-full h-24 p-3 rounded-xl bg-black/40 border border-white/10 text-sm text-muted-foreground focus:outline-none focus:border-primary/50 resize-none"
                defaultValue={"github.com/royalrew/*\nnews.ycombinator.com\nstripe.com/docs/*"}
              />
            </div>
          </div>

          {/* The Watchdog Planner */}
          <div className="p-8 glass rounded-3xl border border-white/5 flex flex-col gap-6">
            <h2 className="text-xl font-bold flex items-center gap-3">
              <Zap className="text-purple-500" />
              The Watchdog Planner
            </h2>

            <div className="space-y-3">
              <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Schemalagda Uppdrag</h3>
              {[
                { schedule: 'Varje timme', desc: 'Läs RSS efter nya GRC-lagar' },
                { schedule: 'Kl 04:00', desc: 'Rensa temp-filer & städa RAM' },
                { schedule: 'Kl 08:00', desc: 'Generera Morning Briefing till Telegram' }
              ].map((task, i) => (
                <div key={i} className="flex gap-3 items-start p-3 bg-white/5 rounded-lg border border-white/5 border-l-2 border-l-purple-500">
                  <div className="text-xs font-mono text-purple-400 mt-0.5 min-w-[70px]">{task.schedule}</div>
                  <div className="text-sm text-gray-300 leading-tight">{task.desc}</div>
                </div>
              ))}
            </div>

            <div className="mt-auto pt-4 border-t border-white/10">
              <h3 className="text-xs font-bold text-red-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                <AlertCircle size={14} /> Goal Override
              </h3>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Injicera nytt högprioriterat mål..."
                  className="flex-1 px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-sm focus:outline-none focus:border-red-500/50"
                />
                <button className="px-4 py-2 bg-red-500/20 hover:bg-red-500/40 text-red-400 font-bold rounded-lg border border-red-500/30 transition-colors">
                  KÖR OVERRIDE
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
