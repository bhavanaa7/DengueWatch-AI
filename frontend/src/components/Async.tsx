import type { ReactNode } from 'react';
import type { ApiState } from '../hooks/useApi';
import ErrorState from './ErrorState';
import LoadingState from './LoadingState';

export default function Async<T>({ state, children }: { state: ApiState<T>; children: (data: T) => ReactNode }) {
  if (state.loading && !state.data) return <LoadingState />;
  if (state.error) return <ErrorState message={state.error} />;
  if (!state.data) return null;
  return <>{children(state.data)}</>;
}
