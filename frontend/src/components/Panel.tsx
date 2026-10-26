import { Paper, Typography } from '@mui/material';
import type { ReactNode } from 'react';

export default function Panel({ title, subtitle, children }: { title?: string; subtitle?: string; children: ReactNode }) {
  return (
    <Paper sx={{ p: 2.5 }}>
      {title && <Typography variant="h6">{title}</Typography>}
      {subtitle && <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>{subtitle}</Typography>}
      {children}
    </Paper>
  );
}
