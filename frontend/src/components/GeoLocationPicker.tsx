import { InputNumber, Space, Typography } from 'antd';
import { EnvironmentOutlined } from '@ant-design/icons';

export interface GeoLocation {
  latitude: number | null;
  longitude: number | null;
}

export interface GeoLocationPickerProps {
  value?: GeoLocation;
  onChange?: (value: GeoLocation) => void;
}

export default function GeoLocationPicker({ value, onChange }: GeoLocationPickerProps) {
  const lat = value?.latitude ?? null;
  const lng = value?.longitude ?? null;

  const handleLatChange = (v: number | null) => {
    onChange?.({ latitude: v, longitude: lng });
  };

  const handleLngChange = (v: number | null) => {
    onChange?.({ latitude: lat, longitude: v });
  };

  return (
    <Space direction="vertical" size="small" style={{ width: '100%' }}>
      <Space align="center">
        <EnvironmentOutlined />
        <Typography.Text strong>Coordenadas</Typography.Text>
      </Space>
      <Space size="middle">
        <div>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            Latitude
          </Typography.Text>
          <InputNumber
            value={lat}
            onChange={handleLatChange}
            min={-90}
            max={90}
            step={0.000001}
            precision={6}
            placeholder="-23.550520"
            style={{ width: '100%' }}
          />
        </div>
        <div>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            Longitude
          </Typography.Text>
          <InputNumber
            value={lng}
            onChange={handleLngChange}
            min={-180}
            max={180}
            step={0.000001}
            precision={6}
            placeholder="-46.633308"
            style={{ width: '100%' }}
          />
        </div>
      </Space>
    </Space>
  );
}
