import { Box, CircularProgress, Typography } from '@mui/material';

export default function LoadingState({ message = 'Loading data from the backend…' }: { message?: string }) {
  return (
    <Box role="status" sx={{ py: 6, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
      <CircularProgress size={32} />
      <Typography color="text.secondary">{message}</Typography>
    </Box>
  );
}
