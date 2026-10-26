import { CssBaseline, ThemeProvider } from '@mui/material';
import React from 'react';
import ReactDOM from 'react-dom/client';
import 'leaflet/dist/leaflet.css';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { FilterProvider } from './hooks/FilterContext';
import { theme } from './theme/theme';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <FilterProvider><App /></FilterProvider>
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>,
);
