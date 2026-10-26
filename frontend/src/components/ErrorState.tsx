import { Alert, AlertTitle } from '@mui/material';

export default function ErrorState({ message }: { message: string }) {
  return (
    <Alert severity="error" sx={{ my: 2 }}>
      <AlertTitle>Something went wrong</AlertTitle>
      {message}
      <br />
      If models are missing, train them first: <code>python -m scripts.train_models</code> (from the backend folder).
    </Alert>
  );
}
