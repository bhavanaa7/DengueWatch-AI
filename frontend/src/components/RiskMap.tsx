import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet';
import { palette } from '../theme/theme';
import type { Risk } from '../types';

export interface MapPoint { name: string; lat: number; lon: number; risk: Risk; predicted: number }
const colors: Record<Risk, string> = { Low: palette.teal, Medium: palette.amber, High: palette.red };

/** City-level map only: the dataset has no sub-city geography. */
export default function RiskMap({ points }: { points: MapPoint[] }) {
  return (
    <MapContainer center={[7, -70]} zoom={3} style={{ height: 360, width: '100%', borderRadius: 14 }} scrollWheelZoom={false}>
      <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {points.map((p) => (
        <CircleMarker key={p.name} center={[p.lat, p.lon]} radius={10 + Math.min(p.predicted, 100) / 6}
          pathOptions={{ color: colors[p.risk], fillColor: colors[p.risk], fillOpacity: 0.6 }}>
          <Popup><strong>{p.name}</strong><br />{p.risk} risk · {p.predicted.toFixed(1)} predicted cases</Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
