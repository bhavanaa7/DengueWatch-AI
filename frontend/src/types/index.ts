export type Risk = 'Low' | 'Medium' | 'High';
export interface Thresholds { medium: number; high: number; outbreak: number; n_train_weeks: number }
export interface Forecast {
  city: string; city_name: string; horizon: number; model: string; origin_week: string; target_week: string;
  predicted_cases: number; lower: number; upper: number; risk: Risk; thresholds: Thresholds; interval_note: string;
}
export interface HistoryPoint { week: string; cases: number }
export interface BacktestPoint { origin_week: string; target_week: string; y_true: number; y_pred: number; lower: number; upper: number }
export interface ForecastResponse { forecast: Forecast; history: HistoryPoint[]; backtest_holdout: BacktestPoint[] }
export interface BestModel { city: string; horizon: number; model: string; dev_mae: number }
export interface Metadata {
  app: string; horizons: number[]; artifacts_ready: boolean; cities: { code: string; name: string }[];
  models: string[]; data_range: { start: string; end: string }; best_models: BestModel[]; availability: Record<string, unknown>;
}
export interface Location { code: string; name: string; weeks: number; start: string; end: string; latest_cases: number; lat?: number; lon?: number }
export type MetricRow = Record<string, string | number | null>;
export interface EvaluationResponse {
  validation_cv: MetricRow[]; holdout: MetricRow[]; best_models: BestModel[];
  availability: Record<string, unknown>; notes: Record<string, string>;
}
export interface WeatherPoint {
  week: string; weekofyear: number; total_cases: number; precipitation_amt_mm: number | null; avg_temp_c: number | null;
  reanalysis_relative_humidity_percent: number | null; precip_rmean4: number | null;
}
export interface WeatherResponse {
  series: WeatherPoint[]; seasonal: { weekofyear: number; cases: number; precip: number }[];
  lag_correlation: { variable: string; lag: number; spearman: number }[]; note: string;
}
export interface ImportanceFeature { feature: string; variable: string; kind: string; lag: number | null; importance: number }
export interface Contribution { feature: string; value: number; contribution: number }
export interface ExplanationResponse {
  city: string; horizon: number; model: string; origin_week: string; warning: string;
  global: { available: boolean; reason?: string; method?: string; features?: ImportanceFeature[];
    by_variable?: { variable: string; importance: number }[]; by_lag?: { lag: number; importance: number }[] };
  local: { available: boolean; reason?: string; base_value?: number; contributions?: Contribution[] };
}
export interface RankingRow {
  rank: number; city: string; horizon: number; predicted_cases: number; risk: Risk; target_week: string; model: string;
  priority_score: number; monitoring: string; explanation: string; incidence_per_100k: number | null;
}
export interface RankingResponse { horizon: number; ranking: RankingRow[]; caveat: string; normalised: boolean; population_note: string }
export interface FigureInfo { file: string; title: string; caption: string; group: 'eda' | 'evaluation' }
export interface FiguresResponse { plots: FigureInfo[] }
