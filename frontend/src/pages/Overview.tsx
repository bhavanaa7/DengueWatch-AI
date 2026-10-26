import { Alert, Box, Typography } from '@mui/material';
import { Activity, Gauge, MapPin, Target } from 'lucide-react';
import Async from '../components/Async';
import ForecastChart from '../components/ForecastChart';
import ForecastFilters from '../components/ForecastFilters';
import InsightBox from '../components/InsightBox';
import PageHeader from '../components/PageHeader';
import Panel from '../components/Panel';
import RiskBadge from '../components/RiskBadge';
import RiskPriorityTable from '../components/RiskPriorityTable';
import StatCard from '../components/StatCard';
import WeatherChart from '../components/WeatherChart';
import { useFilters } from '../hooks/FilterContext';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import { modelLabel } from '../utils/format';
import { forecastInsight } from '../utils/insights';

const grid = { display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', sm: 'repeat(2,1fr)', lg: 'repeat(3,1fr)', xl: 'repeat(6,1fr)' } };

export default function Overview() {
  const { city, horizon } = useFilters();
  const locations = useApi(() => api.locations(), []);
  const fc = useApi(() => api.forecast(city, horizon), [city, horizon]);
  const weather = useApi(() => api.weather(city), [city]);
  const ranking = useApi(() => api.riskRanking(horizon), [horizon]);
  return (
    <>
      <PageHeader title="DengueWatch AI" subtitle="Weekly dengue forecasts for the locations in the DrivenData DengAI dataset. Historical observations and model forecasts are shown separately.">
        <ForecastFilters />
      </PageHeader>
      <Alert severity="info" sx={{ mb: 3 }}>Research prototype using retrospective data from two cities. Not a validated public-health decision tool.</Alert>
      <Async state={fc}>
        {(d) => {
          const latest = locations.data?.find((l) => l.name === city);
          return (
            <>
            <Box sx={{ ...grid, mb: 3 }}>
              <StatCard label="Locations" value={locations.data?.length ?? '—'} icon={<MapPin size={14} />} hint="in this dataset" />
              <StatCard label="Horizon" value={`${horizon} wk`} icon={<Target size={14} />} hint={`target week ${d.forecast.target_week}`} />
              <StatCard label="Latest observed" value={latest?.latest_cases ?? '—'} icon={<Activity size={14} />} hint={`week of ${d.forecast.origin_week}`} />
              <StatCard label="Predicted cases" value={d.forecast.predicted_cases.toFixed(1)} icon={<Gauge size={14} />} hint={`${d.forecast.lower.toFixed(1)} – ${d.forecast.upper.toFixed(1)} interval`} />
              <StatCard label="Forecast risk" value={<RiskBadge risk={d.forecast.risk} />} hint={`High ≥ ${d.forecast.thresholds.high.toFixed(1)} cases`} />
              <StatCard label="Best validated model" value={modelLabel(d.forecast.model)} hint="selected on development folds" />
            </Box>
            <InsightBox mb={3} insights={forecastInsight(d.forecast)} />
            </>
          );
        }}
      </Async>
      <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', lg: '3fr 2fr' } }}>
        <Panel title="Observed history, holdout backtest and forecast" subtitle="Solid = observed; dashed = backtest predictions on the final holdout; red dot = forecast for the target week.">
          <Async state={fc}>{(d) => <ForecastChart data={d} />}</Async>
        </Panel>
        <Panel title="Climate and cases (recent)" subtitle="Observed values only.">
          <Async state={weather}>
            {(w) => <WeatherChart data={w.series.slice(-104)} series={[
              { key: 'precip_rmean4', name: 'Rainfall, 4-wk mean (mm)', axis: 'left' },
              { key: 'total_cases', name: 'Cases', axis: 'right' }]} />}
          </Async>
        </Panel>
      </Box>
      <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>Forecast summary by location</Typography>
      <Async state={ranking}>{(r) => <RiskPriorityTable rows={r.ranking} />}</Async>
    </>
  );
}
