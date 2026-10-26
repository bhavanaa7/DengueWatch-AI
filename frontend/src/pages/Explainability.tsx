import { Alert, Box } from '@mui/material';
import Async from '../components/Async';
import FeatureImportanceChart from '../components/FeatureImportanceChart';
import ForecastFilters from '../components/ForecastFilters';
import InsightBox from '../components/InsightBox';
import PageHeader from '../components/PageHeader';
import Panel from '../components/Panel';
import { useFilters } from '../hooks/FilterContext';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import { FEATURE_IMPORTANCE_EXPLAINER } from '../utils/insights';

type Rows = Record<string, string | number>[];

export default function Explainability() {
  const { city, horizon } = useFilters();
  const ex = useApi(() => api.explanations(city, horizon, 'random_forest'), [city, horizon]);
  return (
    <>
      <PageHeader
        title="Explainable AI"
        subtitle="SHAP tree explanations showing how the Random Forest used its inputs."
      >
        <ForecastFilters />
      </PageHeader>
      <InsightBox mb={2} insights={FEATURE_IMPORTANCE_EXPLAINER} />
      <Async state={ex}>
        {(e) => (
          <Box sx={{ display: 'grid', gap: 2 }}>
            <Alert severity="warning">{e.warning}</Alert>
            {!e.global.available ? <Alert severity="info">{e.global.reason}</Alert> : (
              <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', lg: 'repeat(2,1fr)' } }}>
                <Panel title="Top features" subtitle={`Method: ${e.global.method}`}>
                  <FeatureImportanceChart data={(e.global.features ?? []).slice(0, 15) as unknown as Rows} labelKey="feature" valueKey="importance" />
                </Panel>
                <Panel title="Importance by climate variable"><FeatureImportanceChart data={(e.global.by_variable ?? []).slice(0, 12) as unknown as Rows} labelKey="variable" valueKey="importance" /></Panel>
                <Panel title="Importance by lag (weeks)" subtitle="Summed over variables for plain lag features.">
                  <FeatureImportanceChart data={(e.global.by_lag ?? []).map((r) => ({ lag: `lag ${r.lag}`, importance: r.importance })) as Rows} labelKey="lag" valueKey="importance" height={300} />
                </Panel>
                <Panel title={`Latest prediction explained (origin ${e.origin_week})`} subtitle="Positive (teal) pushed the forecast up; negative (red) pushed it down.">
                  {e.local.available && e.local.contributions
                    ? <FeatureImportanceChart signed data={e.local.contributions as unknown as Rows} labelKey="feature" valueKey="contribution" />
                    : <Alert severity="info">{e.local.reason}</Alert>}
                </Panel>
              </Box>
            )}
          </Box>
        )}
      </Async>
    </>
  );
}
