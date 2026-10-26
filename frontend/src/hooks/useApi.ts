import { useEffect, useState } from 'react';
import { errorMessage } from '../services/api';

export interface ApiState<T> { data?: T; loading: boolean; error?: string }

export function useApi<T>(fn: () => Promise<T>, deps: unknown[]): ApiState<T> {
  const [state, setState] = useState<ApiState<T>>({ loading: true });
  useEffect(() => {
    let alive = true;
    setState((s) => ({ ...s, loading: true, error: undefined }));
    fn().then((data) => alive && setState({ data, loading: false }))
      .catch((e) => alive && setState({ loading: false, error: errorMessage(e) }));
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return state;
}
