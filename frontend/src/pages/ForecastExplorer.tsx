import { Alert, Box, Button, Typography } from '@mui/material';
import { Download } from 'lucide-react';
import Async from '../components/Async';
import ForecastChart from '../components/ForecastChart';
import ForecastFilters from '../components/ForecastFilters';
import InsightBox from '../components/InsightBox';
import PageHeader from '../components/PageHeader';
import Panel from '../components/Panel';
import RiskBadge from '../components/RiskBadge';
import StatCard from '../components/StatCard';
import { useFilters } from '../hooks/FilterContext';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import { downloadCsv, modelLabel } from '../utils/format';
import { driverInsight } from '../utils/insights';

export default function ForecastExplorer() {
  const { city, horizon, model } = useFilters();
  const fc = useApi(() => api.forecast(city, horizon, model), [city, horizon, model]);
  const ex = useApi(() => api.explanations(city, horizon, 'random_forest'), [city, horizon]);
  const drivers = ex.data?.local.available ? driverInsight(ex.data.local.contributions) : [];
  return (
    <>
      <PageHeader title="Forecast Explorer" subtitle="Forecast origin = last observed week. The model only sees data up to that week.">
        <ForecastFilters showModel />
      </PageHeader>
      <Async state={fc}>
        {(d) => {
          const f = d.forecast;
          return (
            <>
              <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', sm: 'repeat(2,1fr)', lg: 'repeat(4,1fr)' }, mb: 3 }}>
                <StatCard label="Forecast origin" value={f.origin_week} hint="last observed week" />
                <StatCard label="Target week" value={f.target_week} hint={`${f.horizon} weeks ahead`} />
                <StatCard label="Predicted cases" value={f.predicted_cases.toFixed(1)} hint={`interval ${f.lower.toFixed(1)} – ${f.upper.toFixed(1)}`} />
                <StatCard label="Risk" value={<RiskBadge risk={f.risk} />} hint={`${modelLabel(f.model)} · Medium ≥ ${f.thresholds.medium.toFixed(1)}, High ≥ ${f.thresholds.high.toFixed(1)}`} />
              </Box>
              <InsightBox mb={3} insights={drivers} />
              <Panel title={`${f.city_name}: observed, backtest and forecast`} subtitle={f.interval_note}>
                <ForecastChart data={d} />
                <Button startIcon={<Download size={16} />} variant="outlined" sx={{ mt: 2 }}
                  onClick={() => downloadCsv(`forecast_${f.city}_h${f.horizon}.csv`, [{
                    city: f.city_name, model: f.model, origin_week: f.origin_week, target_week: f.target_week, horizon_weeks: f.horizon,
                    predicted_cases: f.predicted_cases, lower: f.lower, upper: f.upper, risk: f.risk, medium_threshold: f.thresholds.medium, high_threshold: f.thresholds.high }])}>
                  Download forecast CSV
                </Button>
              </Panel>
            </>
          );
        }}
      </Async>
      <Box sx={{ mt: 3 }}>
        <Panel title="What drove this forecast?" subtitle="Per-prediction contributions from the Random Forest at the latest origin.">
          {ex.loading ? <Typography color="text.secondary">Loading explanation…</Typography>
            : ex.data?.local.available && ex.data.local.contributions ? (
              <Box component="ul" sx={{ m: 0, pl: 3 }}>
                {ex.data.local.contributions.slice(0, 6).map((c) => (
                  <li key={c.feature}><code>{c.feature}</code>: {c.contribution >= 0 ? '+' : ''}{c.contribution.toFixed(2)} cases</li>))}
              </Box>
            ) : <Alert severity="info">{ex.data?.local.reason ?? ex.error ?? 'Explanation unavailable.'}</Alert>}
          <Typography variant="caption" color="text.secondary">Contributions describe the model, not causal effects of weather.</Typography>
        </Panel>
      </Box>
    </>
  );
}
