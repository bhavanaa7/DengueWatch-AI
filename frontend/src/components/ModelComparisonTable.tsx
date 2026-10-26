import { Chip, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Tooltip } from '@mui/material';
import type { MetricRow } from '../types';
import { fmt, modelLabel } from '../utils/format';
import { metricTooltips } from '../utils/insights';
import EmptyState from './EmptyState';

const cols: [string, string][] = [['mae', 'MAE'], ['rmse', 'RMSE'], ['precision', 'Outbreak precision'], ['recall', 'Outbreak recall'], ['f1', 'Outbreak F1'], ['false_alarm_rate', 'False-alarm rate'], ['mean_lead_weeks', 'Mean warning lead (wk)']];

const Header = ({ label, tip }: { label: string; tip?: string }) => tip
  ? <Tooltip title={tip} arrow placement="top"><span style={{ cursor: 'help', borderBottom: '1px dotted currentColor' }}>{label}</span></Tooltip>
  : <>{label}</>;

export default function ModelComparisonTable({ rows, label, bestModel }: { rows: MetricRow[]; label: string; bestModel?: string }) {
  if (!rows.length) return <EmptyState message="No metrics for this selection." />;
  const showEpisodes = rows.some((r) => r.episodes !== undefined && r.episodes !== null);
  return (
    <TableContainer component={Paper} sx={{ overflowX: 'auto' }}>
      <Chip label={label} size="small" color="primary" sx={{ m: 1.5 }} />
      <Table size="small">
        <TableHead><TableRow>
          <TableCell>Model</TableCell>{cols.map(([k, h]) => <TableCell key={h} align="right"><Header label={h} tip={metricTooltips[k]} /></TableCell>)}
          {showEpisodes && <TableCell align="right"><Header label="Episodes warned" tip={metricTooltips.episodes} /></TableCell>}
        </TableRow></TableHead>
        <TableBody>
          {rows.map((r) => (
            <TableRow key={String(r.model)} selected={r.model === bestModel}>
              <TableCell>{modelLabel(String(r.model))}{r.model === bestModel && <Chip label="best (validation)" size="small" sx={{ ml: 1 }} color="secondary" />}</TableCell>
              {cols.map(([k]) => <TableCell key={k} align="right">{fmt(r[k] as number | null, 2)}</TableCell>)}
              {showEpisodes && <TableCell align="right">{r.episodes === undefined || r.episodes === null ? '—' : `${r.episodes_detected ?? 0}/${r.episodes}`}</TableCell>}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
