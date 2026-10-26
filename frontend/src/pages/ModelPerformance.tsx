import { Alert, Box, Typography } from '@mui/material';
import Async from '../components/Async';
import FigureGallery from '../components/FigureGallery';
import ForecastFilters from '../components/ForecastFilters';
import InsightBox from '../components/InsightBox';
import ModelComparisonTable from '../components/ModelComparisonTable';
import PageHeader from '../components/PageHeader';
import Panel from '../components/Panel';
import WeatherChart from '../components/WeatherChart';
import { useFilters } from '../hooks/FilterContext';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import type { MetricRow } from '../types';
import { holdoutInsight } from '../utils/insights';

export default function ModelPerformance() {
  const { city, horizon } = useFilters();
  const meta = useApi(() => api.metadata(), []);
  const ev = useApi(() => api.evaluation(), []);
  const fc = useApi(() => api.forecast(city, horizon), [city, horizon]);
  const code = meta.data?.cities.find((c) => c.name === city)?.code;
  const pick = (rows: MetricRow[]) => rows.filter((r) => r.city === code && r.horizon === horizon);
  return (
    <>
      <PageHeader title="Model Performance" subtitle="Validation (walk-forward folds, used for model selection) and final holdout (never used for selection) are reported separately."><ForecastFilters /></PageHeader>
      <Async state={ev}>
        {(e) => {
          const best = e.best_models.find((b) => b.city === code && b.horizon === horizon)?.model;
          const hold = pick(e.holdout);
          const bestHold = hold.find((r) => r.model === best);
          const unavailable = Object.keys((e.availability.unavailable as Record<string, string>) ?? {});
          return (
            <Box sx={{ display: 'grid', gap: 3 }}>
              {unavailable.length > 0 && <Alert severity="warning">Some models were unavailable during training (see model_availability.json), e.g. missing statsmodels.</Alert>}
              <InsightBox insights={holdoutInsight(bestHold)} />
              <ModelComparisonTable rows={pick(e.validation_cv)} label="Validation (walk-forward CV mean)" bestModel={best} />
              <ModelComparisonTable rows={hold} label="Final holdout" bestModel={best} />
              <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' } }}>
                <Panel title="Actual vs predicted (final holdout, best validated model)">
                  <Async state={fc}>
                    {(d) => <WeatherChart xKey="target_week" data={d.backtest_holdout.map((b) => ({ ...b, target_week: b.target_week.slice(0, 10) }))}
                      series={[{ key: 'y_true', name: 'Actual', color: '#141A46' }, { key: 'y_pred', name: 'Predicted', color: '#5B5BD6' }]} />}
                  </Async>
                </Panel>
                <Panel title="Outbreak confusion matrix (holdout)" subtitle="Outbreak = at/above a training-derived percentile threshold.">
                  {bestHold ? (
                    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 1, textAlign: 'center' }}>
                      {([['TN', 'tn'], ['FP', 'fp'], ['FN', 'fn'], ['TP', 'tp']] as const).map(([l, k]) => (
                        <Box key={k} sx={{ p: 2, borderRadius: 2, bgcolor: k === 'tp' || k === 'tn' ? '#E6F7F5' : '#FDECEC' }}>
                          <Typography variant="h5">{String(bestHold[k])}</Typography><Typography variant="caption">{l}</Typography>
                        </Box>))}
                    </Box>
                  ) : <Typography color="text.secondary">No holdout data.</Typography>}
                </Panel>
              </Box>
            </Box>
          );
        }}
      </Async>
      <Box sx={{ mt: 3 }}><FigureGallery group="evaluation" /></Box>
    </>
  );
}
