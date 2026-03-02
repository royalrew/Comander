import React from 'react';
import AgentCard from '@/components/AgentCard';
import { HeartPulse, Activity, Flame, UtilityPole } from 'lucide-react';

export default function HealthAgentPage() {
    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex items-end justify-between border-b border-white/5 pb-6">
                <div>
                    <h1 className="text-3xl font-bold steel-text tracking-tight mb-2 flex items-center gap-3">
                        <HeartPulse className="text-primary w-8 h-8" />
                        Health Coach Agent
                    </h1>
                    <p className="text-muted-foreground">Performance metrics, recovery, and physical optimization.</p>
                </div>
                <div className="px-3 py-1 bg-amber-500/10 border border-amber-500/20 rounded-full flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                    <span className="text-xs font-mono text-amber-500 uppercase tracking-wider">Awaiting MCP Data</span>
                </div>
            </div>

            {/* Dashboard Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <AgentCard
                    title="DAILY STEPS"
                    value="0"
                    subtitle="Goal: 10,000"
                    icon={<Activity size={24} />}
                />
                <AgentCard
                    title="SLEEP SCORE"
                    value="--"
                    subtitle="Last Night"
                    icon={<UtilityPole size={24} />}
                />
                <AgentCard
                    title="ACTIVE CALORIES"
                    value="0 kcal"
                    subtitle="Goal: 700 kcal"
                    icon={<Flame size={24} />}
                />
            </div>

            {/* Main Content Area */}
            <div className="glass rounded-2xl border border-white/5 p-8">
                <h2 className="text-xl font-bold steel-text mb-6">Today's Coaching Plan</h2>
                <div className="p-4 bg-black/40 rounded-xl border border-white/5 font-mono text-sm text-gray-300">
                    {"[Awaiting LangGraph JSON Payload]\n\nAgent requires Model Context Protocol (MCP) connection to Apple Health/Oura ring..."}
                </div>
            </div>
        </div>
    );
}
