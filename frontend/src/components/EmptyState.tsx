import { Box, Typography } from '@mui/material';
import { Inbox } from 'lucide-react';

export default function EmptyState({ message = 'No data to display.' }: { message?: string }) {
  return (
    <Box sx={{ py: 5, textAlign: 'center', color: 'text.secondary' }}>
      <Inbox size={28} />
      <Typography sx={{ mt: 1 }}>{message}</Typography>
    </Box>
  );
}
