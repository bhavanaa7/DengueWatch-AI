import axios from 'axios';
import type { EvaluationResponse, ExplanationResponse, FiguresResponse, ForecastResponse, Location, Metadata, RankingResponse, WeatherResponse } from '../types';

export const API_BASE: string = import.meta.env.VITE_API_URL || '/api';
const client = axios.create({ baseURL: API_BASE, timeout: 60000 });

export function errorMessage(e: unknown): string {
  if (axios.isAxiosError(e)) {
    if (e.response) {
      const d = e.response.data?.detail;
      return typeof d === 'string' ? d : `Request failed (${e.response.status}).`;
    }
    return 'Cannot reach the backend. Start it with: uvicorn api.main:app --port 8000 (from the backend folder).';
  }
  return e instanceof Error ? e.message : 'Unexpected error';
}

const get = async <T,>(url: string, params?: Record<string, unknown>) => (await client.get<T>(url, { params })).data;

export const api = {
  metadata: () => get<Metadata>('/metadata'),
  locations: () => get<Location[]>('/locations'),
  forecast: (city: string, horizon: number, model?: string) => get<ForecastResponse>('/forecast', { city, horizon, model: model || undefined }),
  evaluation: () => get<EvaluationResponse>('/evaluation'),
  weather: (city: string) => get<WeatherResponse>('/weather', { city }),
  explanations: (city: string, horizon: number, model: string) => get<ExplanationResponse>('/explanations', { city, horizon, model }),
  figures: () => get<FiguresResponse>('/figures'),
  riskRanking: (horizon: number) => get<RankingResponse>('/risk-ranking', { horizon }),
};
