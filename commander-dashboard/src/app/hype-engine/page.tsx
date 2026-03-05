"use client";

import React, { useState, useRef } from 'react';
import { UploadCloud, Sparkles, Wand2, Image as ImageIcon, Loader2, ArrowRight, Video, FileImage } from 'lucide-react';

export default function HypeEnginePage() {
    const [dragActive, setDragActive] = useState(false);
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
    const [selectedTrack, setSelectedTrack] = useState<'track_a' | 'track_b'>('track_a');

    const [isLoading, setIsLoading] = useState(false);
    const [loadingMessage, setLoadingMessage] = useState("");
    const [generatedPrompt, setGeneratedPrompt] = useState<string | null>(null);
    const [mediaUrl, setMediaUrl] = useState<string | null>(null);
    const [mediaType, setMediaType] = useState<'video' | 'image' | null>(null);
    const [error, setError] = useState<string | null>(null);

    const inputRef = useRef<HTMLInputElement>(null);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFileSelect(e.target.files[0]);
        }
    };

    const handleFileSelect = (file: File) => {
        // Strict allowlist for OpenAI Vision + HEIC (handled by backend Pillow)
        const allowedTypes = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif',
            'image/heic', 'image/heif'
        ];

        if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.heic') && !file.name.toLowerCase().endsWith('.heif')) {
            setError(`Formatet "${file.type || 'okänt'}" stöds inte! Vänligen ladda upp JPEG, PNG, WEBP, GIF eller HEIC.`);
            return;
        }

        setSelectedImage(file);
        setGeneratedPrompt(null);
        setMediaUrl(null);
        setMediaType(null);
        setError(null);

        const reader = new FileReader();
        reader.onloadend = () => {
            setImagePreviewUrl(reader.result as string);
        };
        reader.readAsDataURL(file);
    };

    const onButtonClick = () => {
        inputRef.current?.click();
    };

    const handleGenerate = async () => {
        if (!selectedImage) return;

        setIsLoading(true);
        setError(null);
        setGeneratedPrompt(null);
        setMediaUrl(null);
        setMediaType(null);
        setLoadingMessage("Laddar upp bild...");

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://comander-production.up.railway.app";
            const formData = new FormData();
            formData.append("image", selectedImage);
            formData.append("track", selectedTrack);

            setTimeout(() => setLoadingMessage("Kör Vision Model Analyzer..."), 1000);
            setTimeout(() => setLoadingMessage("Skriver Magisk Prompt..."), 2500);
            setTimeout(() => setLoadingMessage("Renderar i Fal.ai Serverfarm... (Detta tar upp till 1-2 minuter)"), 6000);

            const res = await fetch(`${API_URL}/api/v1/hype/generate`, {
                method: "POST",
                body: formData,
            });

            const data = await res.json();

            if (data.status === "success") {
                setGeneratedPrompt(data.prompt);
                if (data.media_url) {
                    setMediaUrl(data.media_url);
                    setMediaType(data.media_type);
                }
            } else {
                setError(data.message || "Failed to generate prompt");
            }

        } catch (err) {
            console.error(err);
            setError("Connection to API failed. Is the server running?");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-8 animate-fade-in relative pb-32">
            <header className="mb-10 text-center max-w-2xl mx-auto">
                <h1 className="text-4xl md:text-5xl font-black tracking-tighter mb-4 text-transparent bg-clip-text bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500">
                    The Hype Engine
                </h1>
                <p className="text-lg text-muted-foreground">
                    Släpp in en tråkig bild. Låt AI:n hallucinera fram ett viralt mästerverk.
                </p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
                {/* Left Column: Upload & Track Selection */}
                <div className="space-y-6">
                    {/* Track Selection */}
                    <div className="glass p-2 rounded-2xl flex relative overflow-hidden">
                        <div
                            className={`absolute top-2 bottom-2 w-[calc(50%-8px)] rounded-xl bg-gradient-to-r transition-all duration-300 shadow-lg ${selectedTrack === 'track_a'
                                ? "left-2 from-pink-500/20 to-orange-500/20 shadow-pink-500/10 border-pink-500/30"
                                : "left-[calc(50%+4px)] from-blue-500/20 to-emerald-500/20 shadow-blue-500/10 border-blue-500/30"
                                } border`}
                        />
                        <button
                            onClick={() => setSelectedTrack('track_a')}
                            className={`flex-1 flex flex-col items-center justify-center p-4 rounded-xl relative z-10 transition-colors ${selectedTrack === 'track_a' ? 'text-white' : 'text-muted-foreground hover:text-white/80'}`}
                        >
                            <Video className={`mb-2 ${selectedTrack === 'track_a' ? 'text-pink-400' : ''}`} size={24} />
                            <span className="font-bold tracking-widest uppercase text-sm">Track A</span>
                            <span className="text-xs opacity-70 mt-1">Viral Video FX</span>
                        </button>
                        <button
                            onClick={() => setSelectedTrack('track_b')}
                            className={`flex-1 flex flex-col items-center justify-center p-4 rounded-xl relative z-10 transition-colors ${selectedTrack === 'track_b' ? 'text-white' : 'text-muted-foreground hover:text-white/80'}`}
                        >
                            <FileImage className={`mb-2 ${selectedTrack === 'track_b' ? 'text-blue-400' : ''}`} size={24} />
                            <span className="font-bold tracking-widest uppercase text-sm">Track B</span>
                            <span className="text-xs opacity-70 mt-1">Pro Flipper (Image)</span>
                        </button>
                    </div>

                    {/* Drag and Drop Zone */}
                    <div
                        onDragEnter={handleDrag}
                        onDragOver={handleDrag}
                        onDragLeave={handleDrag}
                        onDrop={handleDrop}
                        className={`relative rounded-3xl border-2 border-dashed transition-all duration-300 p-8 flex flex-col items-center justify-center min-h-[400px] overflow-hidden ${dragActive ? "border-purple-500 bg-purple-500/5 shadow-[0_0_50px_rgba(168,85,247,0.1)] scale-[1.02]" : "border-white/10 glass hover:border-white/20"
                            } ${imagePreviewUrl ? 'border-none p-0' : ''}`}
                    >
                        <input
                            ref={inputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleChange}
                            className="hidden"
                        />

                        {imagePreviewUrl ? (
                            <div className="w-full h-full relative group">
                                <img src={imagePreviewUrl} alt="Preview" className="w-full h-full object-cover rounded-3xl" />
                                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-4">
                                    <button onClick={onButtonClick} className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-xl backdrop-blur font-bold tracking-widest uppercase text-sm transition-colors border border-white/10">
                                        Byt Bild
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <>
                                <div className="w-20 h-20 bg-gradient-to-br from-white/5 to-white/10 rounded-full flex items-center justify-center mb-6 shadow-xl border border-white/5">
                                    <UploadCloud size={32} className="text-muted-foreground" />
                                </div>
                                <h3 className="text-xl font-bold mb-2">Dra och släpp bilden här</h3>
                                <p className="text-sm text-muted-foreground max-w-sm text-center mb-8">
                                    JPEG, PNG eller WebP upp till 10MB.
                                </p>
                                <button
                                    onClick={onButtonClick}
                                    className="px-8 py-3 bg-white/5 hover:bg-white/10 text-white font-bold tracking-widest uppercase text-sm rounded-xl transition-colors border border-white/10"
                                >
                                    Välj Fil
                                </button>
                            </>
                        )}
                    </div>
                </div>

                {/* Right Column: Generation Console */}
                <div className="space-y-6 flex flex-col h-full">
                    <div className="glass p-8 rounded-3xl border border-white/5 flex-1 relative overflow-hidden flex flex-col">
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/10">
                            <Sparkles className="text-yellow-500" size={24} />
                            <h2 className="text-xl font-bold">The Magic Console</h2>
                        </div>

                        {!selectedImage && !generatedPrompt && !isLoading && (
                            <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground/50">
                                <ImageIcon size={48} className="mb-4 opacity-50" />
                                <p>Ladda upp en bild för att börja.</p>
                            </div>
                        )}

                        {isLoading && (
                            <div className="flex-1 flex flex-col items-center justify-center animate-in fade-in duration-500">
                                <Loader2 size={40} className="text-purple-500 animate-spin mb-6" />
                                <div className="text-lg font-bold text-white mb-2 blink">{loadingMessage}</div>
                                <div className="w-48 h-1.5 bg-black/40 rounded-full overflow-hidden mt-4 border border-white/5">
                                    <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 w-1/2 rounded-full animate-pulse blur-[1px]"></div>
                                </div>
                            </div>
                        )}

                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-500 text-sm">
                                {error}
                            </div>
                        )}

                        {generatedPrompt && !isLoading && (
                            <div className="flex-1 flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-xs font-bold uppercase tracking-widest text-emerald-400 bg-emerald-400/10 px-3 py-1 rounded-full">
                                        Vision LLM Prompt Genererad
                                    </span>
                                </div>
                                <div className="p-4 bg-black/40 border border-white/10 rounded-2xl relative group mb-4">
                                    <p className="text-sm leading-relaxed text-gray-300 italic">
                                        "{generatedPrompt}"
                                    </p>
                                </div>
                                {mediaUrl ? (
                                    <div className="flex-1 rounded-2xl overflow-hidden border border-white/10 relative bg-black/50">
                                        {mediaType === 'video' ? (
                                            <video src={mediaUrl} controls autoPlay loop className="w-full h-full object-cover" />
                                        ) : (
                                            <img src={mediaUrl} alt="AI Generated" className="w-full h-full object-cover" />
                                        )}
                                        <a href={mediaUrl} target="_blank" rel="noreferrer" className="absolute top-4 right-4 p-2 bg-black/80 hover:bg-black rounded-lg text-xs font-bold tracking-widest uppercase transition-colors text-white border border-white/20">
                                            Ladda Ner
                                        </a>
                                    </div>
                                ) : (
                                    <div className="flex-1 border border-white/10 rounded-2xl flex items-center justify-center p-6 text-center text-red-400 bg-red-500/10">
                                        Kunde inte generera media från Fal.ai. Kontrollera API-nyckeln i serverns loggar.
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Action Panel */}
                    <div className="glass p-6 rounded-3xl border border-white/5">
                        {generatedPrompt ? (
                            <button
                                onClick={() => {
                                    setGeneratedPrompt(null);
                                    setMediaUrl(null);
                                    setSelectedImage(null);
                                    setImagePreviewUrl(null);
                                }}
                                className="w-full py-4 rounded-xl font-bold tracking-widest uppercase flex items-center justify-center gap-3 transition-all bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30"
                            >
                                <Sparkles size={18} /> Kör En Ny Bild
                            </button>
                        ) : (
                            <button
                                onClick={handleGenerate}
                                disabled={!selectedImage || isLoading}
                                className={`w-full py-4 rounded-xl font-bold tracking-widest uppercase flex items-center justify-center gap-3 transition-all ${!selectedImage || isLoading
                                    ? "bg-white/5 text-muted-foreground cursor-not-allowed"
                                    : "bg-white text-black hover:bg-gray-200 shadow-[0_0_30px_rgba(255,255,255,0.2)]"
                                    }`}
                            >
                                <Wand2 size={18} />
                                Generera Magi
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
