import { Paper, Typography } from '@mui/material';
import type { ReactNode } from 'react';

export default function StatCard({ label, value, hint, icon }: { label: string; value: ReactNode; hint?: string; icon?: ReactNode }) {
  return (
    <Paper sx={{ p: 2.5, height: '100%' }}>
      <Typography variant="overline" color="text.secondary" sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>{icon}{label}</Typography>
      <Typography variant="h5" component="div" sx={{ mt: 0.5 }}>{value}</Typography>
      {hint && <Typography variant="caption" color="text.secondary">{hint}</Typography>}
    </Paper>
  );
}
