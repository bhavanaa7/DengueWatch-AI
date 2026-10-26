import { Chip } from '@mui/material';
import { palette } from '../theme/theme';
import type { Risk } from '../types';

const colors: Record<Risk, string> = { Low: palette.teal, Medium: palette.amber, High: palette.red };

export default function RiskBadge({ risk }: { risk: Risk }) {
  return <Chip label={`${risk} risk`} size="small" sx={{ bgcolor: colors[risk], color: '#fff', fontWeight: 700 }} />;
}
