"use client";

import React, { useEffect, useState } from 'react';
import { Activity } from 'lucide-react';

export default function FinanceCard({ initialData }: { initialData?: any }) {
    const [data, setData] = useState(initialData);

    useEffect(() => {
        const fetchFinance = async () => {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://comander-production.up.railway.app';
            try {
                const res = await fetch(`${API_URL}/api/v1/cfo/status`);
                if (res.ok) setData(await res.json());
            } catch (err) {
                // Silently fail, keep old data
            }
        };
        const interval = setInterval(fetchFinance, 10000); // 10s poll
        return () => clearInterval(interval);
    }, []);

    const spend = data?.current_spend_usd !== undefined ? data.current_spend_usd.toFixed(2) : '0.00';
    const limit = data?.max_spend_usd !== undefined ? data.max_spend_usd.toFixed(2) : '5.00';
    const spendPercentage = data ? Math.min((data.current_spend_usd / data.max_spend_usd) * 100, 100) : 0;
    const isDanger = spendPercentage > 80;

    return (
        <div className="p-6 rounded-3xl glass border border-white/5 relative overflow-hidden flex flex-col justify-center">
            <div className="absolute top-0 left-0 h-1.5 bg-black/40 w-full">
                <div
                    className={`h-full ${isDanger ? 'bg-red-500 shadow-[0_0_12px_theme(colors.red.500)]' : 'bg-emerald-500 shadow-[0_0_12px_theme(colors.emerald.500)]'} transition-all duration-1000 ease-in-out`}
                    style={{ width: `${spendPercentage}%` }}
                />
            </div>
            <div className="flex items-center justify-between mt-2">
                <div>
                    <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-1 flex items-center gap-2">
                        CFO Token Spend (Idag)
                        {!data && <span className="text-[10px] text-red-400 bg-red-400/10 px-1.5 py-0.5 rounded border border-red-400/20 animate-pulse">Offline</span>}
                    </h3>
                    <p className={`text-4xl font-bold tracking-tighter ${isDanger ? 'text-red-400' : 'text-emerald-400'}`}>${spend}</p>
                    <p className="text-xs text-muted-foreground mt-2 font-mono">/ ${limit} Daglig Budget Gräns</p>
                </div>
                <div className={`p-4 rounded-full ${isDanger ? 'bg-red-500/10 border border-red-500/20' : 'bg-emerald-500/10 border border-emerald-500/20'}`}>
                    <Activity className={isDanger ? 'text-red-500' : 'text-emerald-500'} size={32} />
                </div>
            </div>
        </div>
    );
}
