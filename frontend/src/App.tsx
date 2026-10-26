import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import About from './pages/About';
import Explainability from './pages/Explainability';
import ForecastExplorer from './pages/ForecastExplorer';
import ModelPerformance from './pages/ModelPerformance';
import Overview from './pages/Overview';
import RiskPriority from './pages/RiskPriority';
import WeatherIntelligence from './pages/WeatherIntelligence';

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Overview />} />
        <Route path="forecast" element={<ForecastExplorer />} />
        <Route path="weather" element={<WeatherIntelligence />} />
        <Route path="performance" element={<ModelPerformance />} />
        <Route path="explain" element={<Explainability />} />
        <Route path="risk" element={<RiskPriority />} />
        <Route path="about" element={<About />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
