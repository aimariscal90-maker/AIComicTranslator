import { useState, useRef, useEffect, useCallback } from 'react';
import api from '@/services/api';
import { Job } from '@/types/api';

interface UsePollingOptions {
    interval?: number;
    maxAttempts?: number;
    onComplete?: (job: Job) => void;
    onFail?: (error: string) => void;
    onProgress?: (job: Job) => void;
}

export function usePolling({
    interval = 2000,
    maxAttempts = 300, // 10 minutes default approx
    onComplete,
    onFail,
    onProgress
}: UsePollingOptions = {}) {
    const [isPolling, setIsPolling] = useState(false);
    const [job, setJob] = useState<Job | null>(null);
    const [error, setError] = useState<string | null>(null);
    const attempts = useRef(0);
    const timeoutRef = useRef<NodeJS.Timeout | null>(null);

    const stopPolling = useCallback(() => {
        setIsPolling(false);
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
            timeoutRef.current = null;
        }
    }, []);

    const poll = useCallback(async (jobId: string) => {
        try {
            const { data } = await api.get<Job>(`/jobs/${jobId}`);
            setJob(data);

            if (onProgress) onProgress(data);

            if (data.status === 'completed') {
                stopPolling();
                if (onComplete) onComplete(data);
            } else if (data.status === 'failed') {
                stopPolling();
                const errMsg = data.error || 'Job failed largely';
                setError(errMsg);
                if (onFail) onFail(errMsg);
            } else {
                // Continue polling
                attempts.current += 1;
                if (attempts.current >= maxAttempts) {
                    stopPolling();
                    setError('Timeout: Max attempts reached');
                    if (onFail) onFail('Timeout');
                } else {
                    timeoutRef.current = setTimeout(() => poll(jobId), interval);
                }
            }
        } catch (err: any) {
            stopPolling();
            const errMsg = err.message || 'Network Error';
            setError(errMsg);
            if (onFail) onFail(errMsg);
        }
    }, [interval, maxAttempts, onComplete, onFail, onProgress, stopPolling]);

    const startPolling = useCallback((jobId: string) => {
        attempts.current = 0;
        setIsPolling(true);
        setError(null);
        poll(jobId);
    }, [poll]);

    // Cleanup on unmount
    useEffect(() => {
        return () => stopPolling();
    }, [stopPolling]);

    return {
        startPolling,
        stopPolling,
        isPolling,
        job,
        error
    };
}
