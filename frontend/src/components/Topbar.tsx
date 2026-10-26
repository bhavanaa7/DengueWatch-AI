import { AppBar, Chip, IconButton, Toolbar, Typography } from '@mui/material';
import { Menu } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { useFilters } from '../hooks/FilterContext';
import { NAV } from '../layouts/nav';

export default function Topbar({ onMenu }: { onMenu: () => void }) {
  const { pathname } = useLocation();
  const { city, horizon } = useFilters();
  const title = NAV.find((n) => n.path === pathname)?.title ?? 'DengueWatch AI';
  return (
    <AppBar position="sticky" color="inherit" elevation={0} sx={{ borderBottom: '1px solid #E3E7F1' }}>
      <Toolbar sx={{ gap: 1.5 }}>
        <IconButton aria-label="open navigation" onClick={onMenu} sx={{ display: { md: 'none' } }}><Menu /></IconButton>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>{title}</Typography>
        <Chip label={city} size="small" color="primary" variant="outlined" />
        <Chip label={`${horizon}-week horizon`} size="small" color="secondary" variant="outlined" />
      </Toolbar>
    </AppBar>
  );
}
