import { Box, Typography } from '@mui/material';
import type { ReactNode } from 'react';

export default function PageHeader({ title, subtitle, children }: { title: string; subtitle?: string; children?: ReactNode }) {
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h4" sx={{ color: 'primary.dark' }}>{title}</Typography>
      {subtitle && <Typography color="text.secondary" sx={{ mt: 0.5, maxWidth: 820 }}>{subtitle}</Typography>}
      {children && <Box sx={{ mt: 2 }}>{children}</Box>}
    </Box>
  );
}
