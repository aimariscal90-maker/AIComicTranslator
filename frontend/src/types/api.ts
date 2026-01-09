export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface Box {
    x: number;
    y: number;
    w: number;
    h: number;
}

export interface Bubble {
    bbox: [number, number, number, number]; // x1, y1, x2, y2
    text: string;
    translation: string;
    clean_text?: string;
    bubble_type?: 'speech' | 'thought' | 'sfx' | 'caption';
    translation_provider?: string;
    font?: string;
}

export interface ProcessingResult {
    id: string;
    filename: string;
    original_url: string;
    final_url?: string;
    debug_url?: string;
    clean_url?: string;
    clean_bubble_url?: string;
    bubbles_count: number;
    bubbles_data: Bubble[];
}

export interface Job {
    id: string;
    status: JobStatus;
    progress: number;
    step: string;
    result?: ProcessingResult;
    error?: string;
    created_at?: string;
}

export interface Project {
    id: string;
    name: string;
    created_at: string;
    pages?: ComicPage[];
}

export interface ComicPage {
    id: string;
    page_number: number;
    status: JobStatus;
    original_url: string;
    final_url?: string;
    filename: string;
}
