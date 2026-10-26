import { Paper, Typography } from '@mui/material';
import { Info } from 'lucide-react';
import { Fragment } from 'react';
import { palette } from '../theme/theme';

/** Renders **bold** markers in an insight sentence; everything else is plain text. */
function withBold(text: string) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith('**') && part.endsWith('**') && part.length > 4
      ? <strong key={i}>{part.slice(2, -2)}</strong>
      : <Fragment key={i}>{part}</Fragment>);
}

export default function InsightBox({ insights, title = 'What this means', mb = 0 }: { insights: string[]; title?: string; mb?: number }) {
  if (!insights.length) return null;
  return (
    <Paper role="note" aria-label={title} sx={{ p: 2, mb, bgcolor: '#F2F3FD', borderLeft: `4px solid ${palette.purple}` }}>
      <Typography variant="overline" sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'primary.main', fontWeight: 700, lineHeight: 1.8 }}>
        <Info size={14} aria-hidden />{title}
      </Typography>
      {insights.map((text, i) => (
        <Typography key={i} variant="body2" sx={{ mt: i === 0 ? 0 : 0.75 }}>{withBold(text)}</Typography>
      ))}
    </Paper>
  );
}
