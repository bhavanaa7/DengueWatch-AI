export const fmt = (v: number | null | undefined, digits = 1) =>
  v === null || v === undefined || Number.isNaN(v) ? '—' : v.toFixed(digits);

export const modelLabel = (m: string) =>
  ({ seasonal_naive: 'Seasonal naive', recent_mean4: '4-week mean', negbin: 'Negative Binomial', sarimax: 'SARIMAX', random_forest: 'Random Forest', xgboost: 'XGBoost' } as Record<string, string>)[m] ?? m;

export function toCsv(rows: Record<string, string | number | null>[]): string {
  if (!rows.length) return '';
  const cols = Object.keys(rows[0]);
  return [cols.join(','), ...rows.map((r) => cols.map((c) => JSON.stringify(r[c] ?? '')).join(','))].join('\n');
}

export function downloadCsv(name: string, rows: Record<string, string | number | null>[]) {
  const url = URL.createObjectURL(new Blob([toCsv(rows)], { type: 'text/csv' }));
  const a = document.createElement('a');
  a.href = url; a.download = name; a.click();
  URL.revokeObjectURL(url);
}
