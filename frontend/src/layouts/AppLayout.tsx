import { Box, Drawer } from '@mui/material';
import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';

const W = 260;

export default function AppLayout() {
  const [open, setOpen] = useState(false);
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Drawer variant="permanent" sx={{ display: { xs: 'none', md: 'block' }, '& .MuiDrawer-paper': { width: W, border: 0 } }} open>
        <Sidebar />
      </Drawer>
      <Drawer variant="temporary" open={open} onClose={() => setOpen(false)} sx={{ display: { md: 'none' }, '& .MuiDrawer-paper': { width: W } }}>
        <Sidebar onNavigate={() => setOpen(false)} />
      </Drawer>
      <Box sx={{ flexGrow: 1, ml: { md: `${W}px` }, minWidth: 0 }}>
        <Topbar onMenu={() => setOpen(true)} />
        <Box component="main" sx={{ p: { xs: 2, md: 4 } }}><Outlet /></Box>
      </Box>
    </Box>
  );
}
