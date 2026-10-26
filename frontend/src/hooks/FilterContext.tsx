import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

interface Filters { city: string; horizon: number; model: string; setCity: (c: string) => void; setHorizon: (h: number) => void; setModel: (m: string) => void }
const Ctx = createContext<Filters | null>(null);

export function FilterProvider({ children }: { children: ReactNode }) {
  const [city, setCity] = useState('San Juan');
  const [horizon, setHorizon] = useState(4);
  const [model, setModel] = useState(''); // '' = best validated model
  const value = useMemo(() => ({ city, horizon, model, setCity, setHorizon, setModel }), [city, horizon, model]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useFilters() {
  const v = useContext(Ctx);
  if (!v) throw new Error('useFilters must be used inside FilterProvider');
  return v;
}
