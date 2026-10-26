import { FormControl, InputLabel, MenuItem, Select, Stack } from '@mui/material';
import { useFilters } from '../hooks/FilterContext';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import { modelLabel } from '../utils/format';

export default function ForecastFilters({ showModel = false }: { showModel?: boolean }) {
  const { city, horizon, model, setCity, setHorizon, setModel } = useFilters();
  const meta = useApi(() => api.metadata(), []).data;
  const cities = meta?.cities.map((c) => c.name) ?? ['San Juan', 'Iquitos'];
  const horizons = meta?.horizons ?? [1, 2, 4, 8];
  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel id="city-l">City</InputLabel>
        <Select labelId="city-l" label="City" value={city} onChange={(e) => setCity(e.target.value)}>
          {cities.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
        </Select>
      </FormControl>
      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel id="h-l">Horizon</InputLabel>
        <Select labelId="h-l" label="Horizon" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))}>
          {horizons.map((h) => <MenuItem key={h} value={h}>{h} week{h > 1 ? 's' : ''} ahead</MenuItem>)}
        </Select>
      </FormControl>
      {showModel && (
        <FormControl size="small" sx={{ minWidth: 190 }}>
          <InputLabel id="m-l">Model</InputLabel>
          <Select labelId="m-l" label="Model" value={model} onChange={(e) => setModel(e.target.value)}>
            <MenuItem value="">Best validated</MenuItem>
            {(meta?.models ?? []).map((m) => <MenuItem key={m} value={m}>{modelLabel(m)}</MenuItem>)}
          </Select>
        </FormControl>
      )}
    </Stack>
  );
}
