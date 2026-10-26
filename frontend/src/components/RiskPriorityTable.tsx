import { Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import type { RankingRow } from '../types';
import EmptyState from './EmptyState';
import RiskBadge from './RiskBadge';

export default function RiskPriorityTable({ rows }: { rows: RankingRow[] }) {
  if (!rows.length) return <EmptyState message="No ranking available." />;
  return (
    <TableContainer component={Paper} sx={{ overflowX: 'auto' }}>
      <Table size="small">
        <TableHead><TableRow>
          {['Rank', 'Location', 'Target week', 'Predicted cases', 'Incidence / 100k', 'Risk', 'Priority score', 'Monitoring category', 'Why'].map((h) => <TableCell key={h}>{h}</TableCell>)}
        </TableRow></TableHead>
        <TableBody>
          {rows.map((r) => (
            <TableRow key={r.city}>
              <TableCell>{r.rank}</TableCell><TableCell>{r.city}</TableCell><TableCell>{r.target_week}</TableCell>
              <TableCell>{r.predicted_cases.toFixed(1)}</TableCell>
              <TableCell>{r.incidence_per_100k === null ? '—' : r.incidence_per_100k.toFixed(1)}</TableCell>
              <TableCell><RiskBadge risk={r.risk} /></TableCell>
              <TableCell>{r.priority_score}</TableCell><TableCell>{r.monitoring}</TableCell><TableCell>{r.explanation}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
