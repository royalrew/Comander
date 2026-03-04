import React from 'react';
import { HeartPulse } from 'lucide-react';
import HealthClient from '@/components/HealthClient';

export default function HealthAgentPage() {
    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex items-end justify-between border-b border-white/5 pb-6">
                <div>
                    <h1 className="text-3xl font-bold steel-text tracking-tight mb-2 flex items-center gap-3">
                        <HeartPulse className="text-emerald-500 w-8 h-8" />
                        The Health Coach
                    </h1>
                    <p className="text-muted-foreground">Elite physical and mental optimization driven by biological telemetry.</p>
                </div>
                <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-xs font-mono text-emerald-500 uppercase tracking-wider">Coach Active</span>
                </div>
            </div>

            <HealthClient />
        </div>
    );
}
