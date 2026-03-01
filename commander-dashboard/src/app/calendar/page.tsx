import React from 'react';
import CalendarClient from '@/components/CalendarClient';

export const dynamic = 'force-dynamic';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

async function getCalendarEvents() {
    try {
        const res = await fetch(`${API_URL}/api/v1/calendar`, {
            cache: 'no-store',
            next: { revalidate: 0 }
        });
        if (!res.ok) throw new Error('API down');
        return res.json();
    } catch (e) {
        return null;
    }
}

export default async function CalendarPage() {
    const data = await getCalendarEvents();
    return <CalendarClient initialEvents={data?.events || []} hasError={!data} />;
}
