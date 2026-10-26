import { Box, List, ListItemButton, ListItemIcon, ListItemText, Typography } from '@mui/material';
import { Activity, BarChart3, BrainCircuit, CloudRain, Info, LayoutDashboard, ShieldAlert } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { NAV } from '../layouts/nav';
import { palette } from '../theme/theme';

const icons = [LayoutDashboard, Activity, CloudRain, BarChart3, BrainCircuit, ShieldAlert, Info];

export default function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <Box sx={{ height: '100%', bgcolor: palette.navy, color: '#fff', p: 2 }}>
      <Box sx={{ px: 1, py: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 800 }}>DengueWatch AI</Typography>
        <Typography variant="caption" sx={{ opacity: 0.7 }}>Explainable Dengue Forecasting &amp; Early-Warning Intelligence</Typography>
      </Box>
      <List>
        {NAV.map((n, i) => {
          const Icon = icons[i];
          return (
            <ListItemButton key={n.path} component={NavLink} to={n.path} end={n.path === '/'} onClick={onNavigate}
              sx={{ borderRadius: 2, mb: 0.5, color: 'rgba(255,255,255,0.8)', '&.active': { bgcolor: palette.purple, color: '#fff' } }}>
              <ListItemIcon sx={{ color: 'inherit', minWidth: 36 }}><Icon size={18} /></ListItemIcon>
              <ListItemText primary={n.label} />
            </ListItemButton>
          );
        })}
      </List>
    </Box>
  );
}
