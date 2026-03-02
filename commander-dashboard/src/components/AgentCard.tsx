import React from 'react';

interface AgentCardProps {
    title: string;
    value: React.ReactNode;
    subtitle?: string;
    icon?: React.ReactNode;
    description?: React.ReactNode;
}

export default function AgentCard({ title, value, subtitle, icon, description }: AgentCardProps) {
    return (
        <div className="glass p-6 rounded-2xl border border-white/5 shadow-lg relative overflow-hidden group hover:border-white/10 transition-colors">
            {/* Background Glow */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-primary/10 transition-colors" />

            <div className="flex justify-between items-start mb-4 relative z-10">
                <div>
                    <h3 className="text-sm font-medium text-muted-foreground tracking-wide font-sans">{title}</h3>
                    <div className="mt-2 text-3xl font-bold text-white font-mono tracking-tight">{value}</div>
                    {subtitle && <p className="text-xs text-primary mt-1 font-mono">{subtitle}</p>}
                </div>
                {icon && (
                    <div className="p-3 bg-white/5 rounded-xl border border-white/5 text-muted-foreground group-hover:text-primary transition-colors">
                        {icon}
                    </div>
                )}
            </div>

            {description && (
                <div className="mt-4 pt-4 border-t border-white/5 text-sm text-gray-400 relative z-10 leading-relaxed font-sans">
                    {description}
                </div>
            )}
        </div>
    );
}
