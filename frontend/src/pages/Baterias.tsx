import { useCallback, useEffect, useState } from 'react';
import { Button, Col, Form, Input, message, Popconfirm, Row, Select, Space, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { BateriaResponse, BateriaCreate, BateriaUpdate } from '../types/bateria';
import type { DroneResponse } from '../types/drone';
import type { BateriaStatus } from '../types/enums';

const { Title, Text } = Typography;

const BATERIA_STATUS_OPTIONS: { value: BateriaStatus; label: string }[] = [
  { value: 'DISPONIVEL', label: 'Disponível' },
  { value: 'EM_USO', label: 'Em Uso' },
  { value: 'CARREGANDO', label: 'Carregando' },
  { value: 'REPROVADA', label: 'Reprovada' },
  { value: 'DESCARTADA', label: 'Descartada' },
];

export default function Baterias() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<BateriaResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [filterStatus, setFilterStatus] = useState<BateriaStatus | undefined>();
  const [filterDrone, setFilterDrone] = useState<number | undefined>();
  const [filterAtivo, setFilterAtivo] = useState<boolean | undefined>();
  const [drones, setDrones] = useState<{ value: number; label: string }[]>([]);

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  useEffect(() => {
    apiClient.get<{ items: DroneResponse[] }>('/drones', { params: { page_size: 100 } })
      .then(({ data }) => setDrones(data.items.map((d) => ({ value: d.id, label: d.identificacao }))));
  }, []);

  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (record: BateriaResponse) => { setEditing(record); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); };

  const handleSubmit = async (values: BateriaCreate & BateriaUpdate) => {
    setSaving(true);
    try {
      if (editing) {
        await apiClient.put(`/baterias/${editing.id}`, values);
        message.success('Bateria atualizada com sucesso.');
      } else {
        await apiClient.post('/baterias', values);
        message.success('Bateria criada com sucesso.');
      }
      closeModal();
      refresh();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao salvar bateria.');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleAtivo = async (record: BateriaResponse) => {
    try {
      await apiClient.patch(`/baterias/${record.id}`, { ativo: !record.ativo });
      message.success(record.ativo ? 'Bateria desativada.' : 'Bateria ativada.');
      refresh();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao alterar status.');
    }
  };

  const droneLabel = (id: number | null) => {
    if (!id) return '—';
    return drones.find((d) => d.value === id)?.label ?? `#${id}`;
  };

  const columns: ColumnsType<BateriaResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    { title: 'Identificação', dataIndex: 'identificacao', key: 'identificacao' },
    { title: 'Drone', dataIndex: 'drone_id', key: 'drone_id', render: (id: number | null) => droneLabel(id) },
    { title: 'Ciclos', dataIndex: 'ciclos', key: 'ciclos', width: 90 },
    {
      title: 'Status', dataIndex: 'status', key: 'status', width: 140,
      render: (status: string) => <StatusBadge status={status} />,
    },
    {
      title: 'Ativo', dataIndex: 'ativo', key: 'ativo', width: 90,
      render: (ativo: boolean) => <StatusBadge status={ativo ? 'ATIVO' : 'INATIVO'} />,
    },
    {
      title: 'Ações', key: 'acoes', width: 180,
      render: (_, record) => (
        <Space>
          <Button size="small" onClick={() => openEdit(record)}>Editar</Button>
          <Popconfirm
            title={record.ativo ? 'Desativar esta bateria?' : 'Ativar esta bateria?'}
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
  if (filterStatus) extraParams.status = filterStatus;
  if (filterDrone !== undefined) extraParams.drone_id = filterDrone;
  if (filterAtivo !== undefined) extraParams.ativo = filterAtivo;

  return (
    <div>
      <Title level={2}>Baterias</Title>
      <Text type="secondary">Gestão de baterias dos drones.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Select
          placeholder="Filtrar por status"
          allowClear
          style={{ width: 180 }}
          options={BATERIA_STATUS_OPTIONS}
          onChange={(v) => setFilterStatus(v)}
        />
        <Select
          placeholder="Filtrar por drone"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 200 }}
          options={drones}
          onChange={(v) => setFilterDrone(v)}
        />
        <Select
          placeholder="Filtrar por ativo"
          allowClear
          style={{ width: 160 }}
          options={[{ value: true, label: 'Ativo' }, { value: false, label: 'Inativo' }]}
          onChange={(v) => setFilterAtivo(v)}
        />
      </Space>

      <DataTable<BateriaResponse>
        columns={columns}
        apiUrl="/baterias"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Nova Bateria
          </Button>
        }
      />

      <FormModal<BateriaCreate & BateriaUpdate>
        open={modalOpen}
        title={editing ? 'Editar Bateria' : 'Nova Bateria'}
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        initialValues={
          editing
            ? {
                identificacao: editing.identificacao,
                drone_id: editing.drone_id,
                status: editing.status,
                observacoes: editing.observacoes,
              }
            : undefined
        }
      >
        <Form.Item name="identificacao" label="Identificação" rules={[{ required: true, message: 'Informe a identificação' }]}>
          <Input maxLength={120} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="drone_id" label="Drone (opcional)">
              <Select options={drones} allowClear showSearch optionFilterProp="label" placeholder="Nenhum" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="status" label="Status">
              <Select options={BATERIA_STATUS_OPTIONS} placeholder="Selecione" />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item name="observacoes" label="Observações">
          <Input.TextArea rows={3} />
        </Form.Item>
      </FormModal>
    </div>
  );
}
