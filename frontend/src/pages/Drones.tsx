import { useCallback, useState } from 'react';
import { Button, Col, Form, Input, InputNumber, message, Popconfirm, Row, Select, Space, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { DroneResponse, DroneCreate, DroneUpdate } from '../types/drone';
import type { DroneStatus } from '../types/enums';

const { Title, Text } = Typography;

const DRONE_STATUS_OPTIONS: { value: DroneStatus; label: string }[] = [
  { value: 'DISPONIVEL', label: 'Disponível' },
  { value: 'EM_USO', label: 'Em Uso' },
  { value: 'EM_MANUTENCAO', label: 'Em Manutenção' },
  { value: 'BLOQUEADO', label: 'Bloqueado' },
  { value: 'INATIVO', label: 'Inativo' },
];

export default function Drones() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<DroneResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [filterStatus, setFilterStatus] = useState<DroneStatus | undefined>();
  const [filterAtivo, setFilterAtivo] = useState<boolean | undefined>();

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (record: DroneResponse) => { setEditing(record); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); };

  const handleSubmit = async (values: DroneCreate & DroneUpdate) => {
    setSaving(true);
    try {
      if (editing) {
        await apiClient.put(`/drones/${editing.id}`, values);
        message.success('Drone atualizado com sucesso.');
      } else {
        await apiClient.post('/drones', values);
        message.success('Drone criado com sucesso.');
      }
      closeModal();
      refresh();
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Erro ao salvar drone.');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleAtivo = async (record: DroneResponse) => {
    try {
      await apiClient.patch(`/drones/${record.id}`, { ativo: !record.ativo });
      message.success(record.ativo ? 'Drone desativado.' : 'Drone ativado.');
      refresh();
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Erro ao alterar status.');
    }
  };

  const columns: ColumnsType<DroneResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    { title: 'Identificação', dataIndex: 'identificacao', key: 'identificacao' },
    { title: 'Modelo', dataIndex: 'modelo', key: 'modelo' },
    { title: 'Fabricante', dataIndex: 'fabricante', key: 'fabricante', render: (v: string | null) => v || '—' },
    { title: 'Capacidade (L)', dataIndex: 'capacidade_litros', key: 'capacidade_litros', width: 130 },
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
            title={record.ativo ? 'Desativar este drone?' : 'Ativar este drone?'}
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
  if (filterAtivo !== undefined) extraParams.ativo = filterAtivo;

  return (
    <div>
      <Title level={2}>Drones</Title>
      <Text type="secondary">Gestão da frota de drones.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Select
          placeholder="Filtrar por status"
          allowClear
          style={{ width: 200 }}
          options={DRONE_STATUS_OPTIONS}
          onChange={(v) => setFilterStatus(v)}
        />
        <Select
          placeholder="Filtrar por ativo"
          allowClear
          style={{ width: 160 }}
          options={[{ value: true, label: 'Ativo' }, { value: false, label: 'Inativo' }]}
          onChange={(v) => setFilterAtivo(v)}
        />
      </Space>

      <DataTable<DroneResponse>
        columns={columns}
        apiUrl="/drones"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Novo Drone
          </Button>
        }
      />

      <FormModal<DroneCreate & DroneUpdate>
        open={modalOpen}
        title={editing ? 'Editar Drone' : 'Novo Drone'}
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        initialValues={
          editing
            ? {
                identificacao: editing.identificacao,
                modelo: editing.modelo,
                fabricante: editing.fabricante,
                capacidade_litros: editing.capacidade_litros,
                status: editing.status,
              }
            : undefined
        }
      >
        <Form.Item name="identificacao" label="Identificação" rules={[{ required: true, message: 'Informe a identificação' }]}>
          <Input maxLength={120} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="modelo" label="Modelo" rules={[{ required: true, message: 'Informe o modelo' }]}>
              <Input maxLength={120} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="fabricante" label="Fabricante">
              <Input maxLength={120} />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="capacidade_litros" label="Capacidade (litros)" rules={[{ required: true, message: 'Informe a capacidade' }]}>
              <InputNumber min={0} step={0.1} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="status" label="Status">
              <Select options={DRONE_STATUS_OPTIONS} placeholder="Selecione" />
            </Form.Item>
          </Col>
        </Row>
      </FormModal>
    </div>
  );
}
