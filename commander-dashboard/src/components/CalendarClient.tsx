"use client";

import React, { useState } from 'react';
import { Calendar as CalendarIcon, Clock, AlertCircle, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Plus, X } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function CalendarClient({ initialEvents, hasError }: { initialEvents: any[], hasError: boolean }) {
    const router = useRouter();
    const events = initialEvents;

    // View state
    const [currentDate, setCurrentDate] = useState(new Date());

    // Modal state
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedDate, setSelectedDate] = useState("");
    const [formData, setFormData] = useState({
        start_time: "09:00",
        end_time: "",
        description: ""
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const today = new Date();
    const currentMonth = currentDate.getMonth();
    const currentYear = currentDate.getFullYear();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay();
    const startingDay = firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1;
    const daysArray = Array.from({ length: daysInMonth }, (_, i) => i + 1);
    const blanksArray = Array.from({ length: startingDay }, (_, i) => i);
    const monthNames = ["Januari", "Februari", "Mars", "April", "Maj", "Juni", "Juli", "Augusti", "September", "Oktober", "November", "December"];

    const prevYear = () => setCurrentDate(new Date(currentYear - 1, currentMonth, 1));
    const nextYear = () => setCurrentDate(new Date(currentYear + 1, currentMonth, 1));
    const prevMonth = () => setCurrentDate(new Date(currentYear, currentMonth - 1, 1));
    const nextMonth = () => setCurrentDate(new Date(currentYear, currentMonth + 1, 1));

    const openModal = (dateStr: string) => {
        setSelectedDate(dateStr);
        setFormData({ start_time: "09:00", end_time: "", description: "" });
        setIsModalOpen(true);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
        try {
            await fetch(`${API_URL}/api/v1/calendar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    start_date: selectedDate,
                    ...formData
                })
            });
            setIsModalOpen(false);
            router.refresh(); // Refresh RSC data
        } catch (error) {
            console.error("Failed to save event", error);
        }
        setIsSubmitting(false);
    };

    return (
        <div className="space-y-8 animate-fade-in pb-20 relative">
            <header className="mb-10 flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight steel-text flex items-center gap-3">
                        <CalendarIcon className="text-blue-500" size={32} />
                        The Executive Calendar
                    </h1>
                    <p className="mt-2 text-muted-foreground flex items-center gap-2">
                        Systemets övergripande tidshorisont och scheman.
                        {hasError && <span className="text-xs text-red-400 bg-red-400/10 px-2 py-0.5 rounded border border-red-400/20 flex items-center gap-1"><AlertCircle size={12} /> API Offline</span>}
                    </p>
                </div>
                <div className="flex items-center gap-2 bg-black/40 p-2 rounded-xl border border-white/5">
                    <button onClick={prevYear} className="p-1 hover:bg-white/10 rounded-lg transition-colors text-muted-foreground/50 hover:text-muted-foreground">
                        <ChevronsLeft size={16} />
                    </button>
                    <button onClick={prevMonth} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={20} className="text-muted-foreground" />
                    </button>
                    <span className="font-bold text-white uppercase tracking-widest text-sm w-36 text-center">
                        {monthNames[currentMonth]} {currentYear}
                    </span>
                    <button onClick={nextMonth} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronRight size={20} className="text-muted-foreground" />
                    </button>
                    <button onClick={nextYear} className="p-1 hover:bg-white/10 rounded-lg transition-colors text-muted-foreground/50 hover:text-muted-foreground">
                        <ChevronsRight size={16} />
                    </button>
                </div>
            </header>

            <div className="glass rounded-3xl border border-white/5 overflow-hidden shadow-2xl relative z-10">
                <div className="grid grid-cols-7 border-b border-white/5 bg-black/20">
                    {['Mån', 'Tis', 'Ons', 'Tors', 'Fre', 'Lör', 'Sön'].map(day => (
                        <div key={day} className="py-4 text-center text-xs font-bold text-muted-foreground tracking-widest uppercase">
                            {day}
                        </div>
                    ))}
                </div>

                <div className="grid grid-cols-7 bg-black/40">
                    {blanksArray.map((_, index) => (
                        <div key={`blank-${index}`} className="min-h-[120px] p-2 border-r border-b border-white/5 opacity-20" />
                    ))}

                    {daysArray.map(day => {
                        const dateString = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                        const dayEvents = events.filter((e: any) => e.start_date === dateString);
                        const isToday = day === today.getDate();

                        return (
                            <div key={day} className={`min-h-[140px] p-3 border-r border-b border-white/5 relative group transition-colors hover:bg-white/5 ${isToday ? 'bg-blue-500/5' : ''}`}>
                                <div className={`text-sm font-bold flex items-center justify-center w-8 h-8 rounded-full mb-2 ${isToday ? 'bg-blue-500 text-white shadow-[0_0_15px_rgba(59,130,246,0.5)]' : 'text-zinc-500'}`}>
                                    {day}
                                </div>
                                <div className="space-y-1">
                                    {dayEvents.map((evt: any, idx: number) => (
                                        <div key={idx} className="bg-blue-500/10 border border-blue-500/20 rounded px-2 py-1.5 text-xs">
                                            <div className="text-blue-400 font-bold flex items-center gap-1 mb-0.5">
                                                <Clock size={10} />
                                                {evt.start_time} {evt.end_time ? `- ${evt.end_time}` : ''}
                                            </div>
                                            <div className="text-zinc-300 leading-tight line-clamp-2" title={evt.description}>
                                                {evt.description}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button
                                        onClick={() => openModal(dateString)}
                                        className="text-muted-foreground hover:text-white p-1 rounded hover:bg-white/10"
                                    >
                                        <Plus size={16} />
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            <div className="mt-10">
                <h2 className="text-xl font-bold steel-text mb-6">Agenda Lista (Kommande 7 dagarna)</h2>
                <div className="space-y-3">
                    {events.filter((e: any) => {
                        const evtDate = new Date(e.start_date);
                        const diffTime = evtDate.getTime() - today.getTime();
                        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                        return diffDays >= 0 && diffDays <= 7;
                    }).sort((a: any, b: any) => a.start_date.localeCompare(b.start_date) || a.start_time.localeCompare(b.start_time)).map((evt: any, idx: number) => (
                        <div key={idx} className="glass p-4 rounded-2xl border border-white/5 flex items-center gap-6 hover:bg-white/5 transition-colors">
                            <div className="text-center min-w-[80px]">
                                <div className="text-sm font-bold text-blue-400 uppercase tracking-widest">{new Date(evt.start_date).toLocaleDateString('sv-SE', { weekday: 'short' })}</div>
                                <div className="text-2xl font-black text-white">{evt.start_date.split('-')[2]}</div>
                            </div>
                            <div className="w-px h-10 bg-white/10" />
                            <div className="flex-1">
                                <h4 className="text-lg font-bold text-white">{evt.description}</h4>
                                <div className="text-sm text-muted-foreground flex items-center gap-2 mt-1">
                                    <Clock size={14} />
                                    {evt.start_time} {evt.end_time ? `- ${evt.end_time}` : ''}
                                </div>
                            </div>
                            <div>
                                <span className="px-3 py-1 rounded bg-white/5 text-xs uppercase tracking-widest text-muted-foreground font-bold">Inplanerad</span>
                            </div>
                        </div>
                    ))}
                    {events.length === 0 && (
                        <div className="text-center p-8 glass rounded-2xl border border-white/5 text-muted-foreground">
                            Inga inplanerade händelser de närmaste dagarna. Njut av friheten.
                        </div>
                    )}
                </div>
            </div>

            {/* Manual Event Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in zoom-in-95 duration-200">
                    <div className="bg-zinc-900 border border-white/10 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
                        <div className="p-4 border-b border-white/5 flex items-center justify-between bg-black/20">
                            <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                <Plus size={18} className="text-blue-400" />
                                Ny Händelse: {selectedDate}
                            </h3>
                            <button onClick={() => setIsModalOpen(false)} className="text-muted-foreground hover:text-white transition-colors">
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="p-6 space-y-4">
                            <div className="flex gap-4">
                                <div className="flex-1 space-y-1">
                                    <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Starttid</label>
                                    <input required type="time" value={formData.start_time} onChange={(e) => setFormData({ ...formData, start_time: e.target.value })} className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-white focus:border-blue-500 outline-none transition-colors" />
                                </div>
                                <div className="flex-1 space-y-1">
                                    <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Sluttid (Frivillig)</label>
                                    <input type="time" value={formData.end_time} onChange={(e) => setFormData({ ...formData, end_time: e.target.value })} className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-white focus:border-blue-500 outline-none transition-colors" />
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Beskrivning</label>
                                <textarea required rows={3} placeholder="Vad händer då?" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-white focus:border-blue-500 outline-none transition-colors resize-none" />
                            </div>
                            <div className="pt-4">
                                <button disabled={isSubmitting} type="submit" className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm tracking-widest uppercase rounded-xl transition-all disabled:opacity-50 shadow-[0_0_20px_rgba(37,99,235,0.3)]">
                                    {isSubmitting ? "Sparar..." : "Injektera i Hjärnan"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
