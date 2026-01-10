import axios from 'axios';
import { API_URL } from '@/config';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        // 'Content-Type': 'application/json', // REMOVED: Let Axios set this (multipart vs json)
    },
    timeout: 300000, // 5 minutes (AI tasks can be slow if synchronous, though we use polling)
});

// Request Interceptor
api.interceptors.request.use(
    (config) => {
        // You could add Auth tokens here in the future
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response Interceptor
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Professional Error Logging
        if (error.response) {
            console.error('[API Error]', error.response.status, error.response.data);
        } else if (error.request) {
            console.error('[API Network Error]', error.request);
        } else {
            console.error('[API Setup Error]', error.message);
        }
        return Promise.reject(error);
    }
);

export default api;
