import { useCallback, useEffect, useState } from 'react';
import { Button, Col, Form, Input, InputNumber, message, Popconfirm, Row, Select, Space, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { TalhaoResponse, TalhaoCreate, TalhaoUpdate } from '../types/talhao';
import type { PropriedadeResponse } from '../types/propriedade';
import type { CulturaResponse } from '../types/cultura';

const { Title, Text } = Typography;

export default function Talhoes() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<TalhaoResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [filterPropriedade, setFilterPropriedade] = useState<number | undefined>();
  const [filterAtivo, setFilterAtivo] = useState<boolean | undefined>();
  const [propriedades, setPropriedades] = useState<{ value: number; label: string }[]>([]);
  const [culturas, setCulturas] = useState<{ value: number; label: string }[]>([]);

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  useEffect(() => {
    apiClient.get<{ items: PropriedadeResponse[] }>('/propriedades', { params: { page_size: 100 } })
      .then(({ data }) => setPropriedades(data.items.map((p) => ({ value: p.id, label: p.nome }))));
    apiClient.get<{ items: CulturaResponse[] }>('/culturas', { params: { page_size: 100 } })
      .then(({ data }) => setCulturas(data.items.map((c) => ({ value: c.id, label: c.nome }))));
  }, []);

  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (record: TalhaoResponse) => { setEditing(record); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
const handleSubmit = async (values: any) => {
    setSaving(true);
    try {
      const payload = { ...values };
      if (editing) {
        await apiClient.put(`/talhoes/${editing.id}`, payload);
        message.success('Talhão atualizado com sucesso.');
      } else {
        await apiClient.post('/talhoes', payload);
        message.success('Talhão criado com sucesso.');
      }
      closeModal();
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao salvar talhão.');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleAtivo = async (record: TalhaoResponse) => {
    try {
      await apiClient.patch(`/talhoes/${record.id}`, { ativo: !record.ativo });
      message.success(record.ativo ? 'Talhão desativado.' : 'Talhão ativado.');
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao alterar status.');
    }
  };

  const propLabel = (id: number) => propriedades.find((p) => p.value === id)?.label ?? `#${id}`;
  const culturaLabel = (id: number) => culturas.find((c) => c.value === id)?.label ?? `#${id}`;

  const columns: ColumnsType<TalhaoResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    { title: 'Nome', dataIndex: 'nome', key: 'nome' },
    { title: 'Propriedade', dataIndex: 'propriedade_id', key: 'propriedade_id', render: (id: number) => propLabel(id) },
    { title: 'Cultura', dataIndex: 'cultura_id', key: 'cultura_id', render: (id: number) => culturaLabel(id) },
    { title: 'Área (ha)', dataIndex: 'area_hectares', key: 'area_hectares', width: 110 },
    {
      title: 'Status', dataIndex: 'ativo', key: 'ativo', width: 110,
      render: (ativo: boolean) => <StatusBadge status={ativo ? 'ATIVO' : 'INATIVO'} />,
    },
    {
      title: 'Ações', key: 'acoes', width: 180,
      render: (_, record) => (
        <Space>
          <Button size="small" onClick={() => openEdit(record)}>Editar</Button>
          <Popconfirm
            title={record.ativo ? 'Desativar este talhão?' : 'Ativar este talhão?'}
            onConfirm={() => handleToggleAtivo(record)}
            okText="Sim" cancelText="Não"
          >
            <Button size="small" danger={record.ativo}>
              {record.ativo ? 'Desativar' : 'Ativar'}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const extraParams: Record<string, unknown> = {};
  if (filterPropriedade !== undefined) extraParams.propriedade_id = filterPropriedade;
  if (filterAtivo !== undefined) extraParams.ativo = filterAtivo;

  return (
    <div>
      <Title level={2}>Talhões</Title>
      <Text type="secondary">Gestão de talhões e áreas de cultivo.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Select
          placeholder="Filtrar por propriedade"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 240 }}
          options={propriedades}
          onChange={(v) => setFilterPropriedade(v)}
        />
        <Select
          placeholder="Filtrar por status"
          allowClear
          style={{ width: 160 }}
          options={[{ value: true, label: 'Ativo' }, { value: false, label: 'Inativo' }]}
          onChange={(v) => setFilterAtivo(v)}
        />
      </Space>

      <DataTable<TalhaoResponse>
        columns={columns}
        apiUrl="/talhoes"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Novo Talhão
          </Button>
        }
      />

      <FormModal<TalhaoCreate & TalhaoUpdate>
        open={modalOpen}
        title={editing ? 'Editar Talhão' : 'Novo Talhão'}
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        width={700}
        initialValues={
          editing
            ? {
                propriedade_id: editing.propriedade_id,
                nome: editing.nome,
                area_hectares: editing.area_hectares,
                cultura_id: editing.cultura_id,
                latitude: editing.latitude,
                longitude: editing.longitude,
              } as any // eslint-disable-line @typescript-eslint/no-explicit-any
            : undefined
        }
      >
        <Form.Item name="propriedade_id" label="Propriedade" rules={[{ required: true, message: 'Selecione a propriedade' }]}>
          <Select options={propriedades} showSearch optionFilterProp="label" placeholder="Selecione" />
        </Form.Item>
        <Form.Item name="nome" label="Nome" rules={[{ required: true, message: 'Informe o nome' }]}>
          <Input maxLength={150} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="area_hectares" label="Área (ha)" rules={[{ required: true, message: 'Informe a área' }]}>
              <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="cultura_id" label="Cultura" rules={[{ required: true, message: 'Selecione a cultura' }]}>
              <Select options={culturas} showSearch optionFilterProp="label" placeholder="Selecione" />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="latitude" label="Latitude">
              <InputNumber min={-90} max={90} step={0.0000001} style={{ width: '100%' }} placeholder="-23.5505199" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="longitude" label="Longitude">
              <InputNumber min={-180} max={180} step={0.0000001} style={{ width: '100%' }} placeholder="-46.6333094" />
            </Form.Item>
          </Col>
        </Row>
      </FormModal>
    </div>
  );
}
