import { createTheme } from '@mui/material/styles';

export const palette = {
  navy: '#141A46', purple: '#5B5BD6', teal: '#14B8A6', amber: '#F59E0B', red: '#DC2626',
  bg: '#F4F6FB', border: '#E3E7F1', text: '#1F2547', muted: '#6B7390',
};

export const theme = createTheme({
  palette: {
    primary: { main: palette.purple }, secondary: { main: palette.teal },
    warning: { main: palette.amber }, error: { main: palette.red },
    background: { default: palette.bg, paper: '#FFFFFF' }, text: { primary: palette.text, secondary: palette.muted },
  },
  shape: { borderRadius: 14 },
  typography: { fontFamily: 'Inter, system-ui, sans-serif', h4: { fontWeight: 700 }, h5: { fontWeight: 700 }, h6: { fontWeight: 600 } },
  components: {
    MuiPaper: { styleOverrides: { root: { boxShadow: '0 1px 3px rgba(20,26,70,0.08)', border: `1px solid ${palette.border}` } } },
    MuiButton: { styleOverrides: { root: { textTransform: 'none', fontWeight: 600 } } },
  },
});
