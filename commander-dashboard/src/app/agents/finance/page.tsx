import React from 'react';
import AgentCard from '@/components/AgentCard';
import { DollarSign, TrendingUp, CreditCard, PiggyBank, Flame } from 'lucide-react';

export default function FinanceAgentPage() {
    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex items-end justify-between border-b border-white/5 pb-6">
                <div>
                    <h1 className="text-3xl font-bold steel-text tracking-tight mb-2 flex items-center gap-3">
                        <DollarSign className="text-primary w-8 h-8" />
                        CFO Agent
                    </h1>
                    <p className="text-muted-foreground">Financial intelligence, API burn-rate, and revenue metrics.</p>
                </div>
                <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-xs font-mono text-emerald-500 uppercase tracking-wider">Agent Online</span>
                </div>
            </div>

            {/* Dashboard Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <AgentCard
                    title="API BURN RATE"
                    value="$1.24"
                    subtitle="Last 24 Hours (OpenAI)"
                    icon={<Flame size={24} />}
                />
                <AgentCard
                    title="MMR"
                    value="$0.00"
                    subtitle="Monthly Recurring Revenue"
                    icon={<TrendingUp size={24} />}
                />
                <AgentCard
                    title="STRIPE BALANCE"
                    value="$--"
                    subtitle="Awaiting Sync"
                    icon={<PiggyBank size={24} />}
                />
            </div>

            {/* Main Content Area */}
            <div className="glass rounded-2xl border border-white/5 p-8">
                <h2 className="text-xl font-bold steel-text mb-6">Financial Overview</h2>
                <div className="p-4 bg-black/40 rounded-xl border border-white/5 font-mono text-sm text-gray-300">
                    {"[Awaiting LangGraph JSON Payload]\n\nAgent is analyzing cfo.py spending metrics..."}
                </div>
            </div>
        </div>
    );
}
