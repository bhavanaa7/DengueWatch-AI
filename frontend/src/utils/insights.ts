/**
 * Plain-English insight sentences.
 *
 * Pure functions: numbers in, sentences out. Raw metric values are always kept in the sentence
 * (in brackets) so the plain wording never hides the underlying figure. Text may contain **bold**
 * markers, which <InsightBox> renders. Nothing here is hardcoded from a training run: every number
 * comes from the arguments.
 */
import type { Contribution, Forecast, MetricRow, RankingRow, WeatherResponse } from '../types';
import { modelLabel } from './format';

const isNum = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);
const plural = (n: number, one: string, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;
const pct = (v: number) => `${Math.round(v * 100)}%`;
const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
/** Whole numbers for counts of 10 or more, one decimal below that ("about 0.4 cases"). */
const casesText = (v: number) => (Math.abs(v) >= 10 ? String(Math.round(v)) : v.toFixed(1));

// ---------------------------------------------------------------------------------------------
// Column header tooltips (ModelComparisonTable)
// ---------------------------------------------------------------------------------------------
export const metricTooltips: Record<string, string> = {
  mae: 'Average number of cases the model was wrong by each week. Lower is better.',
  rmse: 'Like MAE, but big misses count extra. Lower is better.',
  precision: 'Of the outbreak alerts raised, how many were real. Higher is better.',
  recall: 'Of the real outbreak weeks, how many the model caught. Higher is better.',
  f1: 'One score that balances precision and recall (0 to 1). Higher is better.',
  false_alarm_rate: 'Share of non-outbreak weeks in which the model wrongly raised an alert. Lower is better.',
  mean_lead_weeks: 'On average, how many weeks before an outbreak began the first warning was issued. Higher means earlier warning.',
  episodes: 'Distinct outbreak periods that were warned about in time, out of all outbreak periods in this evaluation.',
};

// ---------------------------------------------------------------------------------------------
// Feature / variable wording
// ---------------------------------------------------------------------------------------------
const VARIABLE_LABELS: Record<string, string> = {
  precipitation_amt_mm: 'rainfall',
  station_precip_mm: 'station rainfall',
  reanalysis_air_temp_k: 'air temperature',
  reanalysis_avg_temp_k: 'daily mean temperature',
  reanalysis_max_air_temp_k: 'maximum air temperature',
  reanalysis_min_air_temp_k: 'minimum air temperature',
  reanalysis_dew_point_temp_k: 'dew-point temperature',
  station_avg_temp_c: 'station temperature',
  reanalysis_relative_humidity_percent: 'relative humidity',
  reanalysis_specific_humidity_g_per_kg: 'specific humidity',
  ndvi_ne: 'vegetation greenness (north-east of the city)',
  ndvi_nw: 'vegetation greenness (north-west of the city)',
};

/** Human wording for a climate variable name; falls back to the raw name without underscores. */
export function variableLabel(variable: string): string {
  return VARIABLE_LABELS[variable] ?? variable.replace(/_/g, ' ');
}

/** Turns a model feature name such as `cases_lag2` or `precipitation_amt_mm_rmean4` into words. */
export function describeFeature(feature: string): string {
  const m = /^(.*)_(lag|rmean|rsum|rstd)(\d+)$/.exec(feature);
  if (!m) return variableLabel(feature);
  const [, base, kind, nStr] = m;
  const n = Number(nStr);
  const what = base === 'cases' ? 'dengue cases' : variableLabel(base);
  if (kind === 'lag') {
    if (n === 0) return base === 'cases' ? 'the most recent weekly case count' : `the latest ${what}`;
    return `${what} from ${plural(n, 'week')} earlier`;
  }
  const span = `the last ${n} weeks`;
  if (kind === 'rmean') return `${what} averaged over ${span}`;
  if (kind === 'rsum') return `${what} added up over ${span}`;
  return `swings in ${what} over ${span}`;
}

// ---------------------------------------------------------------------------------------------
// Overview / Forecast: what the forecast means
// ---------------------------------------------------------------------------------------------
export function forecastInsight(f: Forecast, selection: 'best' | 'chosen' = 'best'): string[] {
  const where = f.city_name ?? f.city;
  const out: string[] = [
    `The model predicts roughly **${casesText(f.predicted_cases)} dengue cases** in ${where} during the week of ${f.target_week}, ` +
      `${plural(f.horizon, 'week')} after the latest data (likely range: ${Math.round(f.lower)} – ${Math.round(f.upper)}).`,
  ];
  const t = f.thresholds;
  if (f.risk === 'High') {
    out.push(`This is classified as **High** risk — at or above this city's High threshold (${t.high.toFixed(0)} cases), which is among the busier weeks in its history.`);
  } else if (f.risk === 'Medium') {
    out.push(`This is classified as **Medium** risk — at or above the typical weekly level for this city (${t.medium.toFixed(0)} cases) but below its High threshold (${t.high.toFixed(0)}).`);
  } else {
    out.push(`This is classified as **Low** risk — below the typical weekly level for this city (${t.medium.toFixed(0)} cases).`);
  }
  out.push(selection === 'best'
    ? `The forecast comes from the ${modelLabel(f.model)} model, which had the lowest average error during validation.`
    : `The forecast was produced by the ${modelLabel(f.model)} model you selected.`);
  return out;
}

// ---------------------------------------------------------------------------------------------
// Model Performance: holdout metrics in words
// ---------------------------------------------------------------------------------------------
const num = (v: unknown) => (isNum(v) ? v : null);

export function holdoutInsight(row: MetricRow | undefined): string[] {
  if (!row) return [];
  const out: string[] = [];
  const mae = num(row.mae);
  const label = modelLabel(String(row.model));
  if (mae !== null) {
    out.push(`On the unseen test period, the best model (${label}) was off by an average of **${casesText(mae)} cases per week** (MAE ${mae.toFixed(1)}).`);
  }

  const tp = num(row.tp), fp = num(row.fp), fn = num(row.fn), tn = num(row.tn);
  const outbreakWeeks = num(row.outbreak_weeks);
  const recall = num(row.recall);
  if (outbreakWeeks === 0) {
    out.push('The test period contained no outbreak weeks, so catching outbreaks could not be assessed.');
  } else if (tp !== null && fn !== null && outbreakWeeks !== null) {
    out.push(`It correctly flagged **${tp} of ${outbreakWeeks} outbreak weeks** and missed ${fn}${recall !== null ? ` (Recall ${pct(recall)})` : ''}.`);
  }

  const far = num(row.false_alarm_rate);
  if (fp !== null && tn !== null) {
    const quiet = fp + tn;
    out.push(fp === 0
      ? `It raised no false alarms across ${quiet} non-outbreak weeks${far !== null ? ` (False-alarm rate ${pct(far)})` : ''}.`
      : `It raised ${plural(fp, 'false alarm')} across ${quiet} non-outbreak weeks — about ${Math.round((far ?? fp / quiet) * 100)} for every 100 quiet weeks${far !== null ? ` (False-alarm rate ${pct(far)})` : ''}.`);
  }

  const precision = num(row.precision);
  if (tp !== null && fp !== null && tp + fp > 0 && precision !== null) {
    out.push(`Of the ${plural(tp + fp, 'outbreak alert')} it raised, ${tp} ${tp === 1 ? 'was' : 'were'} real (Precision ${pct(precision)}).`);
  }

  const episodes = num(row.episodes);
  const detected = num(row.episodes_detected);
  const lead = num(row.mean_lead_weeks);
  if (episodes !== null && episodes > 0 && detected !== null) {
    const eps = `The test period had ${plural(episodes, 'separate outbreak episode')}`;
    if (detected === 0) {
      out.push(`${eps}; none was warned about before it began.`);
    } else if (lead !== null && lead >= 0.05) {
      out.push(`${eps}; ${detected} ${detected === 1 ? 'was' : 'were'} warned about in advance, on average **${lead.toFixed(1)} weeks** before the outbreak began (Mean lead ${lead.toFixed(1)}).`);
    } else {
      out.push(`${eps}; ${detected} ${detected === 1 ? 'was' : 'were'} flagged, but only as the outbreak itself began, so there was no early notice (Mean lead 0.0).`);
    }
  }
  return out;
}

// ---------------------------------------------------------------------------------------------
// Forecast Explorer: what drove this forecast
// ---------------------------------------------------------------------------------------------
const direction = (c: number) => (c >= 0 ? 'up' : 'down');

export function driverInsight(contributions: Contribution[] | undefined | null): string[] {
  const rows = (contributions ?? []).filter((c) => isNum(c.contribution));
  if (!rows.length) return [];
  const sorted = [...rows].sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));
  const [top, ...rest] = sorted;
  const out = [
    `In the Random Forest model's view, the biggest driver of this forecast was **${describeFeature(top.feature)}**, ` +
      `which pushed the prediction ${direction(top.contribution)} by about ${casesText(Math.abs(top.contribution))} cases.`,
  ];
  const next = rest.slice(0, 2);
  if (next.length) {
    out.push(`It was followed by ${next.map((c) => `${describeFeature(c.feature)} (${direction(c.contribution)} by about ${casesText(Math.abs(c.contribution))})`).join(' and ')}.`);
  }
  out.push('These describe how the model reached its number, not proven causes of dengue.');
  return out;
}

// ---------------------------------------------------------------------------------------------
// Weather Intelligence: strongest lag correlation
// ---------------------------------------------------------------------------------------------
function strengthWord(absRho: number) {
  if (absRho < 0.1) return 'very weak';
  if (absRho < 0.3) return 'weak';
  if (absRho < 0.5) return 'moderate';
  return 'strong';
}

export function lagInsight(rows: WeatherResponse['lag_correlation'] | undefined): string[] {
  const valid = (rows ?? []).filter((r) => isNum(r.spearman));
  if (!valid.length) return [];
  const top = valid.reduce((a, b) => (Math.abs(b.spearman) > Math.abs(a.spearman) ? b : a));
  const label = variableLabel(top.variable);
  const when = top.lag === 0 ? 'the same week' : `${plural(top.lag, 'week')} earlier`;
  const sign = top.spearman >= 0 ? 'positive' : 'negative';
  const out = [
    `${cap(label)} from ${when} shows the strongest link to dengue case counts (Spearman ρ = ${top.spearman.toFixed(2)}), a ${strengthWord(Math.abs(top.spearman))} ${sign} association.`,
  ];
  if (Math.abs(top.spearman) >= 0.1) {
    const later = top.lag === 0 ? 'in that same week' : `about ${plural(top.lag, 'week')} later`;
    out.push(`In plain terms: when ${label} is higher than usual, case counts tend to be ${top.spearman >= 0 ? 'higher' : 'lower'} ${later}. This is a statistical association, not proof that ${label} causes dengue.`);
  } else {
    out.push('No climate variable shows a clear link at any lag here, so weather alone is a weak guide to case counts for this city.');
  }
  return out;
}

// ---------------------------------------------------------------------------------------------
// Explainability: what feature importance means (static)
// ---------------------------------------------------------------------------------------------
export const FEATURE_IMPORTANCE_EXPLAINER: string[] = [
  'These bars show which inputs the model relied on most when making its prediction. Longer bars mean more influence.',
  'They describe model behaviour, not proven causes of dengue.',
];

// ---------------------------------------------------------------------------------------------
// Risk & Priority
// ---------------------------------------------------------------------------------------------
export function riskPriorityInsight(rows: RankingRow[] | undefined): string[] {
  if (!rows?.length) return [];
  const out: string[] = [];
  const [first, second] = rows;
  out.push(`**${first.city}** is ranked first (priority score ${first.priority_score.toFixed(1)} out of 100): the forecast is about ${casesText(first.predicted_cases)} cases, a **${first.risk}** risk week.` +
    (second ? ` ${second.city} follows with a score of ${second.priority_score.toFixed(1)} (${second.risk} risk).` : ''));
  out.push("Risk levels compare each forecast with that city's own past weeks: Low means routine monitoring, Medium an elevated watch, and High a priority review. Because every city is judged against its own history, the same number of cases can be High in one city and Low in another.");
  out.push("The priority score (0–100) blends three things: how the forecast compares with the city's High threshold, its risk level, and its share of the combined forecast. It only helps order locations for attention in this prototype; it is not a measure of how dangerous an outbreak is.");
  return out;
}
