import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { palette } from '../theme/theme';
import EmptyState from './EmptyState';

export default function FeatureImportanceChart({ data, labelKey, valueKey, signed = false, height = 380 }:
  { data: Record<string, string | number>[]; labelKey: string; valueKey: string; signed?: boolean; height?: number }) {
  if (!data.length) return <EmptyState message="No importance values available." />;
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ left: 130 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={palette.border} />
        <XAxis type="number" tick={{ fontSize: 11 }} />
        <YAxis type="category" dataKey={labelKey} width={170} tick={{ fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey={valueKey}>
          {data.map((d, i) => <Cell key={i} fill={signed ? (Number(d[valueKey]) >= 0 ? palette.teal : palette.red) : palette.purple} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
