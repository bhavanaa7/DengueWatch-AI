import { Box, Typography } from '@mui/material';
import PageHeader from '../components/PageHeader';
import Panel from '../components/Panel';

const sections: [string, string][] = [
  ['Problem statement', 'Forecast weekly dengue cases 1, 2, 4 and 8 weeks ahead for San Juan (Puerto Rico) and Iquitos (Peru), flag potential outbreak weeks and assign Low/Medium/High risk.'],
  ['Dataset', 'DrivenData DengAI training data (weekly climate/vegetation features and dengue case counts). Source: https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/ . Check the competition terms before redistributing the data.'],
  ['Algorithms', 'Baselines (seasonal naive, 4-week mean), Negative Binomial count regression, Random Forest and XGBoost. Models that cannot be fitted or are not installed are reported as unavailable, never silently replaced.'],
  ['Feature engineering', 'Climate lags up to 12 weeks, rolling means/sums/standard deviations (3, 4, 8, 12 weeks), case lags, annual sine/cosine seasonality. Every feature at forecast origin t uses data up to week t only; targets are shifted within each city.'],
  ['Walk-forward validation', 'Expanding-window folds inside the development period with a gap equal to the horizon so training targets are known before validation origins, plus a final chronological holdout never used for model selection. Imputation and feature selection are fit on training folds only.'],
  ['Metrics', 'MAE, RMSE, R², MASE (persistence scale), outbreak precision/recall/F1, false-alarm rate and missed outbreak weeks. MAPE is not used because case counts can be zero.'],
  ['Risk thresholds', 'Percentiles of each city\'s training-period case counts (configurable). Outbreak threshold = 90th percentile by default. These are prototype definitions, not clinical thresholds.'],
  ['Uncertainty', 'Intervals come from walk-forward residual quantiles. Coverage on the holdout can fall below the nominal level because dengue data are time-dependent and non-stationary.'],
  ['Limitations and intended use', 'Retrospective analysis of two cities for education and portfolio demonstration. Correlation and feature contributions do not prove causation. Not for operational public-health decisions.'],
];

export default function About() {
  return (
    <>
      <PageHeader title="About and Methodology" subtitle="Explainable Dengue Forecasting & Early-Warning Intelligence" />
      <Box sx={{ display: 'grid', gap: 2 }}>
        {sections.map(([t, body]) => <Panel key={t} title={t}><Typography color="text.secondary">{body}</Typography></Panel>)}
      </Box>
    </>
  );
}
