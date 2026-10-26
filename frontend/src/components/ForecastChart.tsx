import { Area, CartesianGrid, ComposedChart, Legend, Line, ReferenceDot, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { palette } from '../theme/theme';
import type { ForecastResponse } from '../types';

interface Row { week: string; cases?: number; backtest?: number; band?: [number, number]; forecast?: number }

export default function ForecastChart({ data }: { data: ForecastResponse }) {
  const rows = new Map<string, Row>();
  const get = (w: string) => { const k = w.slice(0, 10); if (!rows.has(k)) rows.set(k, { week: k }); return rows.get(k)!; };
  data.history.forEach((h) => { get(h.week).cases = h.cases; });
  data.backtest_holdout.forEach((b) => { const r = get(b.target_week); r.backtest = b.y_pred; r.band = [b.lower, b.upper]; });
  const f = data.forecast;
  const fw = f.target_week.slice(0, 10);
  get(fw).forecast = f.predicted_cases;
  const chart = [...rows.values()].sort((a, b) => a.week.localeCompare(b.week));
  return (
    <ResponsiveContainer width="100%" height={340}>
      <ComposedChart data={chart}>
        <CartesianGrid strokeDasharray="3 3" stroke={palette.border} />
        <XAxis dataKey="week" minTickGap={50} tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} label={{ value: 'Weekly cases', angle: -90, position: 'insideLeft', fontSize: 12 }} />
        <Tooltip />
        <Legend />
        <Area dataKey="band" name="Holdout interval" stroke="none" fill={palette.purple} fillOpacity={0.12} />
        <Line dataKey="cases" name="Observed (history)" stroke={palette.navy} dot={false} strokeWidth={2} />
        <Line dataKey="backtest" name="Predicted (holdout backtest)" stroke={palette.purple} dot={false} strokeDasharray="5 3" />
        <ReferenceLine segment={[{ x: fw, y: f.lower }, { x: fw, y: f.upper }]} stroke={palette.amber} strokeWidth={6} ifOverflow="extendDomain" />
        <ReferenceDot x={fw} y={f.predicted_cases} r={7} fill={palette.red} stroke="#fff" strokeWidth={2} ifOverflow="extendDomain" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}