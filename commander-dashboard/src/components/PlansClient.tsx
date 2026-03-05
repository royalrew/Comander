"use client";

import React, { useEffect, useState } from 'react';
import { Target, Rocket, Play, Pause, RefreshCw } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function PlansClient() {
    const router = useRouter();
    const [jobs, setJobs] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<string | null>(null);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://comander-production.up.railway.app';

    const fetchJobs = async () => {
        try {
            const res = await fetch(`${API_URL}/api/v1/plans`);
            const data = await res.json();
            if (data.status === 'success') {
                setJobs(data.jobs);
            }
        } catch (error) {
            console.error("Failed to fetch jobs:", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchJobs();
        const interval = setInterval(fetchJobs, 10000); // Polling every 10s
        return () => clearInterval(interval);
    }, []);

    const handleAction = async (jobId: string, action: 'pause' | 'resume' | 'trigger') => {
        setActionLoading(`${jobId}-${action}`);
        try {
            await fetch(`${API_URL}/api/v1/plans/${jobId}/${action}`, { method: 'POST' });
            await fetchJobs();
            router.refresh();
        } catch (error) {
            console.error(`Failed to execute ${action} on ${jobId}`, error);
        }
        setActionLoading(null);
    };

    const activeJobs = jobs.filter(j => !j.is_paused);
    const pausedJobs = jobs.filter(j => j.is_paused);

    const formatNextRunTime = (isoString: string) => {
        if (!isoString) return 'Paused';
        const date = new Date(isoString);
        return date.toLocaleString('sv-SE', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getJobDescription = (jobId: string) => {
        switch (jobId) {
            case 'watchdog_heartbeat': return 'Bedömer systemets hälsa löpande och flaggar för problem automatiskt.';
            case 'midweek_review': return 'Affärsanalys och sammanfattning av veckans framsteg och ekonomi.';
            case 'morning_briefing': return 'Sammanställer en rapport över nattens händelser och schemat, skickas till Telegram.';
            case 'check_reminders': return 'Övervakar kalendern varje minut för att säkerställa att inga notifikationer missas.';
            case 'github_code_review': return 'AI-granskare som läser genom dina senaste commits och rapporterar sårbarheter eller buggar.';
            default: return 'Autonom agent rutin.';
        }
    };

    return (
        <div className="space-y-8 animate-fade-in">
            <header className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight steel-text flex items-center gap-3">
                        <Target className="text-red-500" size={32} />
                        Watchdog Planner & Mål
                    </h1>
                    <p className="mt-2 text-muted-foreground">
                        Planera proaktiva uppdrag ("Missions") som The Commander ska utföra asynkront.
                    </p>
                </div>
                <button
                    onClick={fetchJobs}
                    className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-500/10 hover:bg-blue-500/20 text-blue-500 rounded-xl border border-blue-500/30 transition-all font-bold tracking-widest uppercase text-sm"
                >
                    <RefreshCw size={18} className={isLoading ? "animate-spin" : ""} />
                    Refresh
                </button>
            </header>

            {isLoading ? (
                <div className="text-center py-20 text-muted-foreground animate-pulse">Laddar AI Scheman...</div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Active Missions */}
                    <div className="p-8 glass rounded-3xl border border-white/5 space-y-6">
                        <div className="flex items-center justify-between pb-4 border-b border-white/10">
                            <h2 className="text-xl font-bold flex items-center gap-2">
                                <Play className="text-emerald-500" size={20} />
                                Aktiva Cykler
                            </h2>
                            <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 rounded-full text-xs font-bold tracking-widest uppercase">
                                {activeJobs.length} Running
                            </span>
                        </div>

                        <div className="space-y-4">
                            {activeJobs.length === 0 ? (
                                <p className="text-sm text-muted-foreground p-4">Inga uppdrag är aktiva.</p>
                            ) : (
                                activeJobs.map(job => (
                                    <div key={job.id} className="p-4 rounded-2xl bg-black/40 border border-emerald-500/20 shadow-[inset_0_0_20px_rgba(16,185,129,0.05)]">
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className="font-bold text-emerald-400">{job.name}</h3>
                                            <span className="text-[10px] px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded uppercase font-bold tracking-wider">
                                                Active
                                            </span>
                                        </div>
                                        <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                                            {getJobDescription(job.id)}
                                        </p>
                                        <div className="flex items-center justify-between">
                                            <div className="text-[10px] font-mono text-gray-400">
                                                <span>Nästa: {formatNextRunTime(job.next_run_time)}</span>
                                            </div>
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={() => handleAction(job.id, 'trigger')}
                                                    disabled={actionLoading !== null}
                                                    className="px-3 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-lg text-[10px] font-bold tracking-widest uppercase transition-colors flex items-center gap-1"
                                                >
                                                    <Rocket size={12} /> Inject
                                                </button>
                                                <button
                                                    onClick={() => handleAction(job.id, 'pause')}
                                                    disabled={actionLoading !== null}
                                                    className="px-3 py-1.5 bg-yellow-500/10 hover:bg-yellow-500/20 text-yellow-500 rounded-lg text-[10px] font-bold tracking-widest uppercase transition-colors flex items-center gap-1"
                                                >
                                                    <Pause size={12} /> Paus
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Planned / Paused Missions */}
                    <div className="p-8 glass rounded-3xl border border-white/5 space-y-6">
                        <div className="flex items-center justify-between pb-4 border-b border-white/10">
                            <h2 className="text-xl font-bold flex items-center gap-2 text-muted-foreground">
                                <Pause size={20} />
                                Vilande / Pausade
                            </h2>
                            <span className="px-3 py-1 bg-gray-500/10 text-gray-400 rounded-full text-xs font-bold tracking-widest uppercase">
                                {pausedJobs.length} Paused
                            </span>
                        </div>

                        <div className="space-y-4">
                            {pausedJobs.length === 0 ? (
                                <p className="text-sm text-muted-foreground p-4">Inga uppdrag är pausade.</p>
                            ) : (
                                pausedJobs.map(job => (
                                    <div key={job.id} className="p-4 rounded-2xl bg-black/40 border border-white/5 opacity-60">
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className="font-bold text-white">{job.name}</h3>
                                            <span className="text-[10px] px-2 py-0.5 bg-gray-500/20 text-gray-400 rounded uppercase font-bold tracking-wider">Paused</span>
                                        </div>
                                        <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                                            {getJobDescription(job.id)}
                                        </p>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => handleAction(job.id, 'resume')}
                                                disabled={actionLoading !== null}
                                                className="px-3 py-1.5 bg-white/5 hover:bg-white/10 rounded-lg text-[10px] font-bold tracking-widest uppercase transition-colors flex items-center gap-1"
                                            >
                                                <Play size={12} /> Aktivera
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                </div>
            )}
        </div>
    );
}
