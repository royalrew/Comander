import React from 'react';
import AgentCard from '@/components/AgentCard';
import { Cpu, GitBranch, Terminal, ShieldAlert } from 'lucide-react';

export default function TechAgentPage() {
    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex items-end justify-between border-b border-white/5 pb-6">
                <div>
                    <h1 className="text-3xl font-bold steel-text tracking-tight mb-2 flex items-center gap-3">
                        <Cpu className="text-primary w-8 h-8" />
                        Tech Lead Agent
                    </h1>
                    <p className="text-muted-foreground">Architectural oversight, code audits, and system stability.</p>
                </div>
                <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-xs font-mono text-emerald-500 uppercase tracking-wider">Agent Online</span>
                </div>
            </div>

            {/* Dashboard Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <AgentCard
                    title="SYSTEM STATUS"
                    value="100%"
                    subtitle="All services operational"
                    icon={<Terminal size={24} />}
                />
                <AgentCard
                    title="RECENT COMMITS"
                    value="10"
                    subtitle="In the last 72 hours"
                    icon={<GitBranch size={24} />}
                />
                <AgentCard
                    title="OVERNIGHT AUDITS"
                    value="Passed"
                    subtitle="No critical vulnerabilities"
                    icon={<ShieldAlert size={24} />}
                />
            </div>

            {/* Main Content Area */}
            <div className="glass rounded-2xl border border-white/5 p-8">
                <h2 className="text-xl font-bold steel-text mb-6">Latest Audit Report</h2>
                <div className="p-4 bg-black/40 rounded-xl border border-white/5 font-mono text-sm text-gray-300 whitespace-pre-wrap">
                    {"[Awaiting LangGraph JSON Payload]\n\nAgent is standing by for GitHub data injection..."}
                </div>
            </div>
        </div>
    );
}
