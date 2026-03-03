"use client";

import React, { useState } from 'react';
import { Calendar as CalendarIcon, Clock, AlertCircle, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Plus, X, Bell } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function CalendarClient({ initialEvents, hasError }: { initialEvents: any[], hasError: boolean }) {
    const router = useRouter();
    const events = initialEvents;

    // View state
    const [currentDate, setCurrentDate] = useState(new Date());
    const [viewMode, setViewMode] = useState<'month' | 'week' | 'day'>('month');

    // Modal state
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedDate, setSelectedDate] = useState("");
    const [editingEventId, setEditingEventId] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        start_time: "09:00",
        end_time: "",
        description: "",
        category: "General",
        priority: "Medium",
        location: "",
        agent_id: "",
        color: "",
        is_reminder: true
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

    const openModal = (dateStr: string, existingEvent: any = null) => {
        setSelectedDate(dateStr);
        if (existingEvent) {
            setFormData({
                start_time: existingEvent.start_time,
                end_time: existingEvent.end_time || "",
                description: existingEvent.description,
                category: existingEvent.category || "General",
                priority: existingEvent.priority || "Medium",
                location: existingEvent.location || "",
                agent_id: existingEvent.agent_id || "",
                color: existingEvent.color || "",
                is_reminder: existingEvent.is_reminder !== false // Default to true if undefined
            });
            setEditingEventId(existingEvent.id);
        } else {
            setFormData({
                start_time: "09:00",
                end_time: "",
                description: "",
                category: "General",
                priority: "Medium",
                location: "",
                agent_id: "",
                color: "",
                is_reminder: true
            });
            setEditingEventId(null);
        }
        setIsModalOpen(true);
    };

    const getCategoryColor = (category: string, overrideColor?: string) => {
        if (overrideColor) return overrideColor;
        switch (category) {
            case 'Health': return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400';
            case 'Finance': return 'border-amber-500/30 bg-amber-500/10 text-amber-400';
            case 'Work': return 'border-blue-500/30 bg-blue-500/10 text-blue-400';
            case 'Tech': return 'border-purple-500/30 bg-purple-500/10 text-purple-400';
            default: return 'border-zinc-500/30 bg-zinc-500/10 text-zinc-400';
        }
    };

    const getPriorityIcon = (priority: string) => {
        switch (priority) {
            case 'Critical': return <AlertCircle size={12} className="text-red-500" />;
            case 'High': return <div className="w-2 h-2 rounded-full bg-orange-500" />;
            case 'Medium': return <div className="w-2 h-2 rounded-full bg-yellow-500" />;
            default: return <div className="w-2 h-2 rounded-full bg-zinc-500" />;
        }
    };

    const handleDelete = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!editingEventId) return;
        setIsSubmitting(true);
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://comander-production.up.railway.app';
        try {
            await fetch(`${API_URL}/api/v1/calendar/${editingEventId}`, { method: 'DELETE' });
            setIsModalOpen(false);
            router.refresh();
        } catch (error) {
            console.error("Failed to delete event", error);
        }
        setIsSubmitting(false);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://comander-production.up.railway.app';
        try {
            const endpoint = editingEventId ? `${API_URL}/api/v1/calendar/${editingEventId}` : `${API_URL}/api/v1/calendar`;
            const method = editingEventId ? 'PUT' : 'POST';
            await fetch(endpoint, {
                method,
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
                    {/* View Controls */}
                    <div className="flex bg-black/40 rounded-lg overflow-hidden border border-white/5 mr-4">
                        <button onClick={() => setViewMode('month')} className={`px-3 py-1 text-xs font-bold uppercase tracking-widest transition-colors ${viewMode === 'month' ? 'bg-blue-600 text-white' : 'text-muted-foreground hover:bg-white/10'}`}>Månad</button>
                        <button onClick={() => setViewMode('week')} className={`px-3 py-1 text-xs font-bold uppercase tracking-widest transition-colors ${viewMode === 'week' ? 'bg-blue-600 text-white' : 'text-muted-foreground hover:bg-white/10'}`}>Vecka</button>
                        <button onClick={() => setViewMode('day')} className={`px-3 py-1 text-xs font-bold uppercase tracking-widest transition-colors ${viewMode === 'day' ? 'bg-blue-600 text-white' : 'text-muted-foreground hover:bg-white/10'}`}>Dag</button>
                    </div>

                    <button onClick={prevYear} className="p-1 hover:bg-white/10 rounded-lg transition-colors text-muted-foreground/50 hover:text-muted-foreground">
                        <ChevronsLeft size={16} />
                    </button>
                    <button onClick={prevMonth} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={20} className="text-muted-foreground" />
                    </button>
                    <span className="font-bold text-white uppercase tracking-widest text-sm w-36 text-center">
                        {viewMode === 'month' ? `${monthNames[currentMonth]} ${currentYear}` : currentDate.toLocaleDateString('sv-SE', { month: 'short', day: 'numeric' })}
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

                {viewMode === 'month' && (
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
                                        {dayEvents.map((evt: any, idx: number) => {
                                            const catColors = getCategoryColor(evt.category, evt.color);
                                            return (
                                                <div onClick={() => openModal(dateString, evt)} key={idx} className={`border rounded px-2 py-1.5 text-xs cursor-pointer hover:brightness-125 transition-all ${catColors}`}>
                                                    <div className="font-bold flex items-center gap-1 mb-0.5">
                                                        {getPriorityIcon(evt.priority)}
                                                        {evt.start_time} {evt.end_time ? `- ${evt.end_time}` : ''}
                                                        {evt.is_reminder && <Bell size={10} className="ml-auto opacity-70" />}
                                                    </div>
                                                    <div className="leading-tight line-clamp-2" title={evt.description}>
                                                        {evt.description}
                                                    </div>
                                                    {evt.agent_id && (
                                                        <div className="text-[10px] mt-1 opacity-60 uppercase tracking-widest">{evt.agent_id}</div>
                                                    )}
                                                </div>
                                            );
                                        })}
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
                )}

                {/* Week View */}
                {viewMode === 'week' && (
                    <div className="grid grid-cols-7 bg-black/40 min-h-[500px]">
                        {/* Simplified week view - just showing 7 days from current date */}
                        {Array.from({ length: 7 }).map((_, idx) => {
                            const date = new Date(currentDate);
                            date.setDate(currentDate.getDate() - currentDate.getDay() + 1 + idx); // Start from Monday
                            const dateString = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
                            const dayEvents = events.filter((e: any) => e.start_date === dateString);
                            const isToday = date.toDateString() === today.toDateString();

                            return (
                                <div key={`week-${idx}`} className={`p-3 border-r border-white/5 relative group transition-colors hover:bg-white/5 ${isToday ? 'bg-blue-500/5' : ''}`}>
                                    <div className={`text-sm font-bold flex items-center justify-center w-8 h-8 rounded-full mb-4 ${isToday ? 'bg-blue-500 text-white shadow-[0_0_15px_rgba(59,130,246,0.5)]' : 'text-zinc-500'}`}>
                                        {date.getDate()}
                                    </div>
                                    <div className="space-y-2">
                                        {dayEvents.map((evt: any, idx2: number) => {
                                            const catColors = getCategoryColor(evt.category, evt.color);
                                            return (
                                                <div onClick={() => openModal(dateString, evt)} key={idx2} className={`border rounded p-2 text-xs cursor-pointer hover:brightness-125 transition-all ${catColors}`}>
                                                    <div className="font-bold flex items-center gap-1 mb-1">
                                                        {evt.start_time} {evt.end_time ? `- ${evt.end_time}` : ''}
                                                    </div>
                                                    <div className="leading-tight">
                                                        {getPriorityIcon(evt.priority)} <span className="ml-1">{evt.description}</span>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                    <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button onClick={() => openModal(dateString)} className="text-muted-foreground hover:text-white p-1 rounded hover:bg-white/10"><Plus size={16} /></button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}

                {/* Day View */}
                {viewMode === 'day' && (
                    <div className="bg-black/40 min-h-[500px] p-6">
                        <div className="max-w-3xl mx-auto space-y-4">
                            {(() => {
                                const dateString = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}`;
                                const dayEvents = events.filter((e: any) => e.start_date === dateString).sort((a: any, b: any) => a.start_time.localeCompare(b.start_time));

                                if (dayEvents.length === 0) {
                                    return (
                                        <div className="text-center py-20 text-muted-foreground border border-dashed border-white/10 rounded-2xl flex flex-col items-center justify-center gap-4">
                                            <p>Inga händelser schemalagda för denna dag.</p>
                                            <button onClick={() => openModal(dateString)} className="px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-sm font-bold tracking-widest uppercase transition-colors flex items-center gap-2">
                                                <Plus size={16} /> Lägg till Händelse
                                            </button>
                                        </div>
                                    );
                                }

                                return dayEvents.map((evt: any, idx: number) => {
                                    const catColors = getCategoryColor(evt.category, evt.color);
                                    return (
                                        <div onClick={() => openModal(dateString, evt)} key={`day-${idx}`} className={`p-4 rounded-xl border cursor-pointer hover:brightness-125 transition-all flex items-start gap-4 ${catColors}`}>
                                            <div className="font-black text-lg min-w-[80px] pt-1">
                                                {evt.start_time}
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2 mb-1">
                                                    {getPriorityIcon(evt.priority)}
                                                    <h3 className="text-lg font-bold">{evt.description}</h3>
                                                </div>
                                                <div className="flex items-center gap-4 text-sm opacity-80 mt-2">
                                                    {evt.location && <span className="flex items-center gap-1"><Clock size={14} />{evt.location}</span>}
                                                    {evt.agent_id && <span className="flex items-center gap-1 uppercase tracking-widest text-xs font-bold border border-current rounded px-2">{evt.agent_id}</span>}
                                                    {evt.is_reminder && <span className="flex items-center gap-1 text-yellow-500"><Bell size={14} /> Reminder</span>}
                                                </div>
                                            </div>
                                        </div>
                                    );
                                });
                            })()}
                        </div>
                    </div>
                )}
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
                        <div onClick={() => openModal(evt.start_date, evt)} key={idx} className="glass p-4 rounded-2xl border border-white/5 flex items-center gap-6 hover:bg-white/5 transition-colors cursor-pointer group">
                            <div className="text-center min-w-[80px]">
                                <div className="text-sm font-bold text-muted-foreground uppercase tracking-widest">{new Date(evt.start_date).toLocaleDateString('sv-SE', { weekday: 'short' })}</div>
                                <div className="text-2xl font-black text-white group-hover:text-blue-400 transition-colors">{evt.start_date.split('-')[2]}</div>
                            </div>
                            <div className={`w-1 h-12 rounded-full ${getCategoryColor(evt.category, evt.color).split(' ')[0].replace('border-', 'bg-')}`} />
                            <div className="flex-1">
                                <h4 className="text-lg font-bold text-white flex items-center gap-2">
                                    {getPriorityIcon(evt.priority)}
                                    {evt.description}
                                </h4>
                                <div className="text-sm text-muted-foreground flex items-center gap-4 mt-1">
                                    <span className="flex items-center gap-1"><Clock size={14} />{evt.start_time} {evt.end_time ? `- ${evt.end_time}` : ''}</span>
                                    {evt.location && <span className="flex items-center gap-1 text-zinc-400"><Clock size={14} />{evt.location}</span>}
                                    {evt.agent_id && <span className="flex items-center gap-1 text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded text-xs uppercase tracking-wider">{evt.agent_id}</span>}
                                    {evt.is_reminder && <span className="flex items-center gap-1 text-yellow-500/80"><Bell size={12} /> Telegram</span>}
                                </div>
                            </div>
                            <div>
                                <span className={`px-3 py-1 rounded text-xs uppercase tracking-widest font-bold ${getCategoryColor(evt.category, evt.color)}`}>{evt.category || 'General'}</span>
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
                                {editingEventId ? `Ändra: ${selectedDate}` : `Ny Händelse: ${selectedDate}`}
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
                                <textarea required rows={2} placeholder="Vad händer då?" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-white focus:border-blue-500 outline-none transition-colors resize-none" />
                            </div>

                            <div className="flex gap-4">
                                <div className="flex-1 space-y-1">
                                    <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Kategori</label>
                                    <select value={formData.category} onChange={(e) => setFormData({ ...formData, category: e.target.value })} className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-white focus:border-blue-500 outline-none transition-colors">
                                        <option value="General">Allmänt</option>
                                        <option value="Work">Arbete</option>
                                        <option value="Health">Hälsa / Träning</option>
                                        <option value="Finance">Ekonomi</option>
                                        <option value="Tech">Teknik / Kod</option>
                                    </select>
                                </div>
                                <div className="flex-1 space-y-1">
                                    <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Prioritet</label>
                                    <select value={formData.priority} onChange={(e) => setFormData({ ...formData, priority: e.target.value })} className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-white focus:border-blue-500 outline-none transition-colors">
                                        <option value="Low">Låg</option>
                                        <option value="Medium">Medium</option>
                                        <option value="High">Hög</option>
                                        <option value="Critical">Kritisk</option>
                                    </select>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <div className="flex-[2] space-y-1">
                                    <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Plats</label>
                                    <input type="text" placeholder="T.ex. Office / Zoom" value={formData.location} onChange={(e) => setFormData({ ...formData, location: e.target.value })} className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-white focus:border-blue-500 outline-none transition-colors" />
                                </div>
                                <div className="flex-1 space-y-1">
                                    <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Agent ID</label>
                                    <input type="text" placeholder="Frivilligt" value={formData.agent_id} onChange={(e) => setFormData({ ...formData, agent_id: e.target.value })} className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-white focus:border-blue-500 outline-none transition-colors" />
                                </div>
                            </div>

                            <label className="flex items-center gap-3 p-3 bg-black/20 border border-white/5 rounded-lg cursor-pointer hover:bg-white/5 transition-colors">
                                <input type="checkbox" checked={formData.is_reminder} onChange={(e) => setFormData({ ...formData, is_reminder: e.target.checked })} className="w-4 h-4 rounded bg-black/40 border-white/10 text-blue-500 focus:ring-blue-500/50" />
                                <div className="flex flex-col">
                                    <span className="text-sm font-bold text-white flex items-center gap-2"><Bell size={14} className="text-yellow-500" /> Telegram-Påminnelse</span>
                                    <span className="text-xs text-muted-foreground">The Commander pingar dig i Telegram exakt kl {formData.start_time}.</span>
                                </div>
                            </label>
                            <div className="pt-4 flex gap-3">
                                {editingEventId && (
                                    <button type="button" onClick={handleDelete} disabled={isSubmitting} className="px-6 py-3 bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 font-bold text-sm tracking-widest uppercase rounded-xl transition-all disabled:opacity-50">
                                        Ta Bort
                                    </button>
                                )}
                                <button disabled={isSubmitting} type="submit" className="flex-1 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm tracking-widest uppercase rounded-xl transition-all disabled:opacity-50 shadow-[0_0_20px_rgba(37,99,235,0.3)]">
                                    {isSubmitting ? "Sparar..." : (editingEventId ? "Uppdatera Händelse" : "Injektera i Hjärnan")}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
