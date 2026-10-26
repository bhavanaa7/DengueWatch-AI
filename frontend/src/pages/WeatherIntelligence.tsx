import { Alert, Box, FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import { useState } from 'react';
import Async from '../components/Async';
import FigureGallery from '../components/FigureGallery';
import FeatureImportanceChart from '../components/FeatureImportanceChart';
import ForecastFilters from '../components/ForecastFilters';
import InsightBox from '../components/InsightBox';
import PageHeader from '../components/PageHeader';
import Panel from '../components/Panel';
import WeatherChart from '../components/WeatherChart';
import { useFilters } from '../hooks/FilterContext';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import { lagInsight } from '../utils/insights';

export default function WeatherIntelligence() {
  const { city, horizon } = useFilters();
  const [variable, setVariable] = useState('');
  const w = useApi(() => api.weather(city), [city]);
  const ex = useApi(() => api.explanations(city, horizon, 'random_forest'), [city, horizon]);
  return (
    <>
      <PageHeader title="Weather Intelligence" subtitle="Observed climate, seasonality and lag associations with dengue cases."><ForecastFilters /></PageHeader>
      <Async state={w}>
        {(d) => {
          const vars = [...new Set(d.lag_correlation.map((r) => r.variable))];
          const active = variable || vars[0] || '';
          const lag = d.lag_correlation.filter((r) => r.variable === active);
          return (
            <>
            <InsightBox mb={2} insights={lagInsight(d.lag_correlation)} />
            <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', lg: 'repeat(2,1fr)' } }}>
              <Panel title="Rainfall vs cases"><WeatherChart data={d.series} series={[{ key: 'precipitation_amt_mm', name: 'Rainfall (mm)' }, { key: 'precip_rmean4', name: '4-wk rolling mean', color: '#14B8A6' }, { key: 'total_cases', name: 'Cases', axis: 'right', color: '#141A46' }]} /></Panel>
              <Panel title="Temperature (°C)"><WeatherChart data={d.series} series={[{ key: 'avg_temp_c', name: 'Avg temperature (°C)', color: '#F59E0B' }]} /></Panel>
              <Panel title="Relative humidity (%)"><WeatherChart data={d.series} series={[{ key: 'reanalysis_relative_humidity_percent', name: 'Humidity (%)', color: '#14B8A6' }]} /></Panel>
              <Panel title="Seasonal pattern" subtitle="Mean by week of year."><WeatherChart data={d.seasonal} xKey="weekofyear" series={[{ key: 'cases', name: 'Mean cases', color: '#141A46' }, { key: 'precip', name: 'Mean rainfall (mm)', axis: 'right', color: '#5B5BD6' }]} /></Panel>
              <Panel title="Lag correlation with cases" subtitle={d.note}>
                <FormControl size="small" sx={{ mb: 1, minWidth: 260 }}>
                  <InputLabel id="v-l">Variable</InputLabel>
                  <Select labelId="v-l" label="Variable" value={active} onChange={(e) => setVariable(e.target.value)}>
                    {vars.map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                  </Select>
                </FormControl>
                <WeatherChart data={lag} xKey="lag" series={[{ key: 'spearman', name: 'Spearman ρ (climate at t−lag vs cases at t)', color: '#5B5BD6' }]} />
              </Panel>
              <Panel title="Model feature importance by variable" subtitle="Random Forest, selected features only.">
                <Async state={ex}>
                  {(e) => e.global.available && e.global.by_variable
                    ? <FeatureImportanceChart data={e.global.by_variable.slice(0, 12) as unknown as Record<string, string | number>[]} labelKey="variable" valueKey="importance" />
                    : <Alert severity="info">{e.global.reason}</Alert>}
                </Async>
              </Panel>
            </Box>
            </>
          );
        }}
      </Async>
      <Box sx={{ mt: 3 }}><FigureGallery group="eda" /></Box>
    </>
  );
}
