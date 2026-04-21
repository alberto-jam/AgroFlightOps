import { useEffect, useState } from 'react';
import {
  Button, Col, Form, InputNumber, Row, Select, Space, Typography, Upload, message,
} from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import DataTable from '../components/DataTable';
import apiClient from '../api/client';
import type { EvidenciaResponse } from '../types/evidencia';
import type { MissaoResponse } from '../types/missao';

const { Title, Text } = Typography;

type DropdownOption = { value: number; label: string };

export default function Evidencias() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [form] = Form.useForm();

  // Filters
  const [filterMissao, setFilterMissao] = useState<number | undefined>();

  // Dropdown data
  const [missoes, setMissoes] = useState<DropdownOption[]>([]);

  useEffect(() => {
    apiClient.get<{ items: MissaoResponse[] }>('/missoes', { params: { page_size: 200 } })
      .then(({ data }) =>
        setMissoes(data.items.map((m) => ({ value: m.id, label: m.codigo }))),
      );
  }, []);

  const lookupLabel = (list: DropdownOption[], id: number) =>
    list.find((o) => o.value === id)?.label ?? `#${id}`;

  const refresh = () => setRefreshKey((k) => k + 1);

  const handleUpload = async () => {
    try {
      const values = await form.validateFields();
      const file = values.file?.[0]?.originFileObj;
      if (!file) {
        message.warning('Selecione um arquivo.');
        return;
      }
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      formData.append('missao_id', String(values.missao_id));
      if (values.latitude != null) formData.append('latitude', String(values.latitude));
      if (values.longitude != null) formData.append('longitude', String(values.longitude));

      await apiClient.post('/evidencias', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      message.success('Evidência enviada com sucesso.');
      form.resetFields();
      refresh();
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Erro ao enviar evidência.');
    } finally {
      setUploading(false);
    }
  };

  const columns: ColumnsType<EvidenciaResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    {
      title: 'Missão', dataIndex: 'missao_id', key: 'missao_id', width: 120,
      render: (id: number) => lookupLabel(missoes, id),
    },
    { title: 'Arquivo', dataIndex: 'nome_arquivo', key: 'nome_arquivo' },
    { title: 'Tipo', dataIndex: 'tipo_arquivo', key: 'tipo_arquivo', width: 120, render: (v: string | null) => v || '—' },
    {
      title: 'Latitude', dataIndex: 'latitude', key: 'latitude', width: 120,
      render: (v: number | null) => v != null ? v.toFixed(6) : '—',
    },
    {
      title: 'Longitude', dataIndex: 'longitude', key: 'longitude', width: 120,
      render: (v: number | null) => v != null ? v.toFixed(6) : '—',
    },
    {
      title: 'Enviada em', dataIndex: 'created_at', key: 'created_at', width: 170,
      render: (d: string) => dayjs(d).format('DD/MM/YYYY HH:mm'),
    },
  ];

  const extraParams: Record<string, unknown> = {};
  if (filterMissao) extraParams.missao_id = filterMissao;

  return (
    <div>
      <Title level={2}>Evidências</Title>
      <Text type="secondary">Evidências de execução de missões.</Text>

      <div style={{ margin: '16px 0', padding: 16, background: '#fafafa', borderRadius: 8 }}>
        <Typography.Title level={5} style={{ marginTop: 0 }}>Enviar Nova Evidência</Typography.Title>
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="missao_id" label="Missão" rules={[{ required: true, message: 'Selecione a missão' }]}>
                <Select options={missoes} showSearch optionFilterProp="label" placeholder="Selecione" />
              </Form.Item>
            </Col>
            <Col span={5}>
              <Form.Item name="latitude" label="Latitude">
                <InputNumber min={-90} max={90} step={0.000001} precision={6} placeholder="-23.550520" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={5}>
              <Form.Item name="longitude" label="Longitude">
                <InputNumber min={-180} max={180} step={0.000001} precision={6} placeholder="-46.633308" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={5}>
              <Form.Item
                name="file"
                label="Arquivo"
                valuePropName="fileList"
                getValueFromEvent={(e) => (Array.isArray(e) ? e : e?.fileList)}
                rules={[{ required: true, message: 'Selecione um arquivo' }]}
              >
                <Upload accept=".jpg,.jpeg,.png,.mp4,.pdf" maxCount={1} beforeUpload={() => false}>
                  <Button icon={<UploadOutlined />}>Selecionar</Button>
                </Upload>
              </Form.Item>
            </Col>
            <Col span={3} style={{ display: 'flex', alignItems: 'flex-end', paddingBottom: 24 }}>
              <Button type="primary" loading={uploading} onClick={handleUpload}>
                Enviar
              </Button>
            </Col>
          </Row>
        </Form>
      </div>

      <Space style={{ margin: '16px 0' }}>
        <Select
          placeholder="Filtrar por Missão"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 200 }}
          options={missoes}
          onChange={(v) => setFilterMissao(v)}
        />
      </Space>

      <DataTable<EvidenciaResponse>
        columns={columns}
        apiUrl="/evidencias"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
      />
    </div>
  );
}
