import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

import Sidebar from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "The Commander | Enterprise GRC Agent",
  description: "Autonomous AI Intelligence Dashboard",
};

import { Menu, Home, Activity, Wrench, FileText, Settings, Key, Command, Brain, LayoutDashboard, ShieldCheck, Database, Calendar } from 'lucide-react';

const navItems = [
  { name: 'Översikt', href: '/', icon: <Home size={20} /> },
  { name: 'Minne & Konvergens', href: '/memory', icon: <Database size={20} /> },
  { name: 'Kalender', href: '/calendar', icon: <Calendar size={20} /> },
  { name: 'Verktyg & Arsenal', href: '/tools', icon: <Wrench size={20} /> },
  { name: 'Mål & Planer', href: '/plans', icon: <Activity size={20} /> },
  { name: 'Inställningar', href: '/settings', icon: <Settings size={20} /> },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased bg-black overflow-hidden`}
      >
        <div className="flex h-screen w-full relative">

          {/* Animated Background Elements */}
          <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
            <div className="absolute top-[-10%] left-[10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[120px] animate-pulse" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600/10 blur-[120px] animate-pulse" style={{ animationDelay: '2s' }} />
          </div>

          <Sidebar />

          <main className="flex-1 relative z-10 overflow-y-auto overflow-x-hidden p-8">
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </main>

        </div>
      </body>
    </html>
  );
}
