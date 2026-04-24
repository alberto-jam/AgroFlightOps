import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { AlertTriangle, Battery, Gauge, MapPinned, Route } from 'lucide-react';
import './style.css';

type FeatureCollection = any;

const SAMPLE_URL = '/sample-track.geojson';

function metric(features: any[]) {
  const line = features.find(f => f.geometry?.type === 'LineString');
  const points = features.filter(f => f.geometry?.type === 'Point');
  const avgScore = line?.properties?.avg_score ?? 0;
  const distanceM = line?.properties?.distance_m ?? 0;
  const anomalies = points.filter(p => p.properties?.anomaly_reasons).length;
  const minBattery = points.reduce((m, p) => Math.min(m, p.properties?.battery_percent ?? 100), 100);
  return { avgScore, distanceM, anomalies, minBattery, sampledPoints: points.length };
}

function App() {
  const [url, setUrl] = useState(SAMPLE_URL);
  const [geojson, setGeojson] = useState<FeatureCollection | null>(null);
  const [error, setError] = useState('');

  async function loadGeoJson() {
    setError('');
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setGeojson(await res.json());
    } catch (e: any) {
      setError(`Falha ao carregar GeoJSON: ${e.message}`);
    }
  }

  useEffect(() => { loadGeoJson(); }, []);

  useEffect(() => {
    if (!geojson) return;
    const container = L.DomUtil.get('map');
    if (container != null) (container as any)._leaflet_id = null;
    const map = L.map('map');
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: 'OpenStreetMap' }).addTo(map);
    const layer = L.geoJSON(geojson, {
      pointToLayer: (_feature, latlng) => L.circleMarker(latlng, { radius: 4 }),
      onEachFeature: (feature, layer) => {
        if (feature.geometry?.type === 'Point') {
          const p = feature.properties || {};
          layer.bindPopup(`Score: ${p.mission_score}<br/>Vel.: ${p.speed_mps} m/s<br/>Bat.: ${p.battery_percent}%<br/>${p.anomaly_reasons || 'Sem anomalia'}`);
        }
      }
    }).addTo(map);
    map.fitBounds(layer.getBounds(), { padding: [20, 20] });
    return () => { map.remove(); };
  }, [geojson]);

  const m = useMemo(() => geojson ? metric(geojson.features || []) : null, [geojson]);
  const anomalyPoints = useMemo(() => (geojson?.features || []).filter((f: any) => f.geometry?.type === 'Point' && f.properties?.anomaly_reasons).slice(0, 20), [geojson]);

  return <div className="page">
    <header>
      <div>
        <h1>Agrotech DJI Agras Analytics</h1>
        <p>MVP de telemetria, mapa de voo, score de missão e anomalias operacionais.</p>
      </div>
    </header>

    <section className="loader">
      <input value={url} onChange={e => setUrl(e.target.value)} placeholder="URL do track.geojson" />
      <button onClick={loadGeoJson}>Carregar GeoJSON</button>
    </section>
    {error && <div className="error">{error}</div>}

    {m && <section className="cards">
      <Card icon={<Gauge/>} title="Score médio" value={`${m.avgScore}`} />
      <Card icon={<Route/>} title="Distância" value={`${(m.distanceM/1000).toFixed(2)} km`} />
      <Card icon={<Battery/>} title="Bateria mínima" value={`${m.minBattery}%`} />
      <Card icon={<AlertTriangle/>} title="Pontos anômalos" value={`${m.anomalies}`} />
      <Card icon={<MapPinned/>} title="Pontos amostrados" value={`${m.sampledPoints}`} />
    </section>}

    <main className="grid">
      <section className="panel mapPanel"><h2>Mapa de trajeto</h2><div id="map" /></section>
      <section className="panel"><h2>Anomalias detectadas</h2><div className="table">
        {anomalyPoints.map((f: any, i: number) => <div className="row" key={i}>
          <strong>{f.properties.timestamp}</strong>
          <span>{f.properties.anomaly_reasons}</span>
          <small>Score {f.properties.mission_score} · Vel {f.properties.speed_mps} m/s · Bat {f.properties.battery_percent}%</small>
        </div>)}
      </div></section>
    </main>
  </div>;
}

function Card({icon, title, value}: any) { return <div className="card"><div className="icon">{icon}</div><div><span>{title}</span><strong>{value}</strong></div></div>; }

createRoot(document.getElementById('root')!).render(<App />);
