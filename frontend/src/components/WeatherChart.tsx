import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { palette } from '../theme/theme';

interface Series { key: string; name: string; color?: string; axis?: 'left' | 'right' }

export default function WeatherChart({ data, xKey = 'week', series, height = 260 }: { data: object[]; xKey?: string; series: Series[]; height?: number }) {
  const hasRight = series.some((s) => s.axis === 'right');
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke={palette.border} />
        <XAxis dataKey={xKey} minTickGap={50} tick={{ fontSize: 11 }} tickFormatter={(v) => String(v).slice(0, 10)} />
        <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
        {hasRight && <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} />}
        <Tooltip />
        <Legend />
        {series.map((s, i) => (
          <Line key={s.key} yAxisId={s.axis ?? 'left'} dataKey={s.key} name={s.name} dot={false} strokeWidth={2}
            stroke={s.color ?? [palette.purple, palette.teal, palette.amber][i % 3]} connectNulls />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
