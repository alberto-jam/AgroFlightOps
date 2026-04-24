import { useEffect, useRef, useState } from 'react';
import { Card, Col, Row, Spin, Statistic, Table, Typography, message } from 'antd';
import {
  AimOutlined,
  DashboardOutlined,
  ThunderboltOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import apiClient from '../api/client';

/* ── Fix default Leaflet marker icons (bundler issue) ── */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

/* ── Types ── */
interface TelemetriaResumo {
  flight_id: string;
  dt: string;
  points: number;
  distance_m: number;
  avg_score: number;
  min_battery: number;
  anomaly_points: number;
}

interface Anomalia {
  timestamp: string;
  latitude: number;
  longitude: number;
  speed_mps: number;
  battery_percent: number;
  height_above_ground_m: number;
  gps_satellites: number;
  signal_strength_percent: number;
  anomaly_reasons: string;
  mission_score: number;
}

interface TelemetriaTabProps {
  missaoId: number;
}

/* ── Helper: score → color ── */
function scoreColor(score: number): string {
  if (score >= 80) return '#52c41a'; // green
  if (score >= 50) return '#faad14'; // yellow
  return '#f5222d'; // red
}

/* ── Sub-component: fly map to a point ── */
function FlyTo({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo([lat, lng], 17, { duration: 0.8 });
  }, [lat, lng, map]);
  return null;
}

/* ── Main component ── */
export default function TelemetriaTab({ missaoId }: TelemetriaTabProps) {
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [resumo, setResumo] = useState<TelemetriaResumo | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [geojson, setGeojson] = useState<any>(null);
  const [anomalias, setAnomalias] = useState<Anomalia[]>([]);
  const [flyTarget, setFlyTarget] = useState<{ lat: number; lng: number } | null>(null);
  const geoJsonRef = useRef<L.GeoJSON | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setNotFound(false);

    const fetchAll = async () => {
      try {
        const [resResumo, resGeo, resAnom] = await Promise.all([
          apiClient.get(`/missoes/${missaoId}/telemetria/resumo`),
          apiClient.get(`/missoes/${missaoId}/telemetria/geojson`),
          apiClient.get(`/missoes/${missaoId}/telemetria/anomalias`),
        ]);
        if (cancelled) return;
        setResumo(resResumo.data);
        setGeojson(resGeo.data);
        setAnomalias(resAnom.data);
      } catch (err: unknown) {
        if (cancelled) return;
        const status = (err as { response?: { status?: number } })?.response?.status;
        if (status === 404) {
          setNotFound(true);
        } else {
          message.error('Erro ao carregar telemetria.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchAll();
    return () => { cancelled = true; };
  }, [missaoId]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 48 }}>
        <Spin size="large" tip="Carregando telemetria..." />
      </div>
    );
  }

  if (notFound) {
    return (
      <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 48 }}>
        Nenhuma telemetria encontrada para esta missão
      </Typography.Text>
    );
  }

  /* ── GeoJSON style callbacks ── */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const pointToLayer = (feature: any, latlng: L.LatLng) => {
    const score: number = feature.properties?.mission_score ?? 50;
    return L.circleMarker(latlng, {
      radius: 5,
      fillColor: scoreColor(score),
      color: '#333',
      weight: 1,
      fillOpacity: 0.85,
    });
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const onEachFeature = (feature: any, layer: L.Layer) => {
    if (feature.geometry?.type === 'Point' && feature.properties) {
      const p = feature.properties;
      layer.bindPopup(
        `<b>Score:</b> ${p.mission_score}<br/>` +
        `<b>Velocidade:</b> ${p.speed_mps?.toFixed(1)} m/s<br/>` +
        `<b>Bateria:</b> ${p.battery_percent}%<br/>` +
        (p.anomaly_reasons ? `<b>Anomalias:</b> ${p.anomaly_reasons}` : ''),
      );
    }
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const geoStyle = (feature?: any) => {
    if (feature?.geometry?.type === 'LineString') {
      return { color: '#1890ff', weight: 3, opacity: 0.8 };
    }
    return {};
  };

  /* ── Compute map center from geojson ── */
  let center: [number, number] = [-15.78, -47.93]; // default Brazil
  if (geojson?.features?.length) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const line = geojson.features.find((f: any) => f.geometry?.type === 'LineString');
    if (line?.geometry?.coordinates?.length) {
      const coords = line.geometry.coordinates;
      const mid = coords[Math.floor(coords.length / 2)];
      center = [mid[1], mid[0]];
    }
  }

  /* ── Anomalias table columns ── */
  const anomColumns: ColumnsType<Anomalia> = [
    {
      title: 'Horário',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (v: string) => {
        try { return new Date(v).toLocaleString('pt-BR'); } catch { return v; }
      },
    },
    {
      title: 'Tipo Anomalia',
      dataIndex: 'anomaly_reasons',
      key: 'anomaly_reasons',
      render: (v: string) => v?.replace(/\|/g, ', ') || '—',
    },
    { title: 'Velocidade (m/s)', dataIndex: 'speed_mps', key: 'speed_mps', width: 130, render: (v: number) => v?.toFixed(1) },
    { title: 'Bateria (%)', dataIndex: 'battery_percent', key: 'battery_percent', width: 110 },
    { title: 'Altura (m)', dataIndex: 'height_above_ground_m', key: 'height_above_ground_m', width: 110, render: (v: number) => v?.toFixed(1) },
    {
      title: 'Score',
      dataIndex: 'mission_score',
      key: 'mission_score',
      width: 80,
      render: (v: number) => (
        <span style={{ color: scoreColor(v), fontWeight: 600 }}>{v}</span>
      ),
    },
  ];

  return (
    <div>
      {/* KPI Cards */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Score Médio"
              value={resumo?.avg_score ?? 0}
              precision={1}
              suffix="/ 100"
              prefix={<DashboardOutlined />}
              valueStyle={{ color: scoreColor(resumo?.avg_score ?? 0) }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Distância Total"
              value={resumo?.distance_m ?? 0}
              precision={0}
              suffix="m"
              prefix={<AimOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Total Anomalias"
              value={resumo?.anomaly_points ?? 0}
              prefix={<WarningOutlined />}
              valueStyle={resumo?.anomaly_points ? { color: '#f5222d' } : undefined}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="Bateria Mínima"
              value={resumo?.min_battery ?? 0}
              suffix="%"
              prefix={<ThunderboltOutlined />}
              valueStyle={
                (resumo?.min_battery ?? 100) < 20 ? { color: '#f5222d' } : undefined
              }
            />
          </Card>
        </Col>
      </Row>

      {/* Leaflet Map */}
      <div style={{ height: 400, marginBottom: 16, borderRadius: 8, overflow: 'hidden' }}>
        <MapContainer
          center={center}
          zoom={15}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {geojson && (
            <GeoJSON
              key={missaoId}
              data={geojson}
              style={geoStyle}
              pointToLayer={pointToLayer}
              onEachFeature={onEachFeature}
              ref={(ref) => { geoJsonRef.current = ref; }}
            />
          )}
          {flyTarget && <FlyTo lat={flyTarget.lat} lng={flyTarget.lng} />}
        </MapContainer>
      </div>

      {/* Anomalias Table */}
      <Typography.Title level={5} style={{ marginBottom: 8 }}>Anomalias</Typography.Title>
      <Table<Anomalia>
        columns={anomColumns}
        dataSource={anomalias}
        rowKey={(r) => `${r.timestamp}-${r.latitude}-${r.longitude}`}
        pagination={{ pageSize: 10 }}
        size="small"
        onRow={(record) => ({
          onClick: () => setFlyTarget({ lat: record.latitude, lng: record.longitude }),
          style: { cursor: 'pointer' },
        })}
      />
    </div>
  );
}
