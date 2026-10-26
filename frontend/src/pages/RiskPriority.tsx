import { Alert, Box, Typography } from '@mui/material';
import Async from '../components/Async';
import ForecastFilters from '../components/ForecastFilters';
import InsightBox from '../components/InsightBox';
import PageHeader from '../components/PageHeader';
import Panel from '../components/Panel';
import RiskMap, { type MapPoint } from '../components/RiskMap';
import RiskPriorityTable from '../components/RiskPriorityTable';
import { useFilters } from '../hooks/FilterContext';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import { riskPriorityInsight } from '../utils/insights';

export default function RiskPriority() {
  const { horizon } = useFilters();
  const r = useApi(() => api.riskRanking(horizon), [horizon]);
  const loc = useApi(() => api.locations(), []);
  return (
    <>
      <PageHeader title="Risk and Priority" subtitle="Prototype ranking of the two dataset locations from model forecasts."><ForecastFilters /></PageHeader>
      <Async state={r}>
        {(d) => {
          const points: MapPoint[] = d.ranking.flatMap((row) => {
            const l = loc.data?.find((x) => x.name === row.city);
            return l?.lat !== undefined && l.lon !== undefined ? [{ name: row.city, lat: l.lat, lon: l.lon, risk: row.risk, predicted: row.predicted_cases }] : [];
          });
          return (
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Alert severity="warning">{d.caveat}</Alert>
              <Alert severity={d.normalised ? 'info' : 'warning'}>{d.population_note}</Alert>
              <InsightBox insights={riskPriorityInsight(d.ranking)} />
              <RiskPriorityTable rows={d.ranking} />
              <Panel title="Location map" subtitle="City-level only; circle colour = forecast risk, size = predicted cases. The dataset has no sub-city geography.">
                {points.length ? <RiskMap points={points} /> : <Typography color="text.secondary">Coordinates unavailable.</Typography>}
              </Panel>
              <Typography variant="body2" color="text.secondary">
                Risk categories use each city's own training-period percentiles (Medium ≥ 50th, High ≥ 80th by default, configurable). They are not medically validated outbreak definitions.
              </Typography>
            </Box>
          );
        }}
      </Async>
    </>
  );
}
