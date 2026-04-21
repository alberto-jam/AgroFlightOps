import { useCallback, useEffect, useState } from 'react';
import { Button, Col, Form, Input, InputNumber, message, Popconfirm, Row, Select, Space, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { PropriedadeResponse, PropriedadeCreate, PropriedadeUpdate } from '../types/propriedade';
import type { ClienteResponse } from '../types/cliente';

const { Title, Text } = Typography;

const ESTADOS = [
  'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS',
  'MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO',
];

export default function Propriedades() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<PropriedadeResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [filterCliente, setFilterCliente] = useState<number | undefined>();
  const [filterAtivo, setFilterAtivo] = useState<boolean | undefined>();
  const [clientes, setClientes] = useState<{ value: number; label: string }[]>([]);

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  useEffect(() => {
    apiClient.get<{ items: ClienteResponse[] }>('/clientes', { params: { page_size: 100 } })
      .then(({ data }) => setClientes(data.items.map((c) => ({ value: c.id, label: c.nome }))));
  }, []);

  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (record: PropriedadeResponse) => { setEditing(record); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); };

  const handleSubmit = async (values: PropriedadeCreate & PropriedadeUpdate) => {
    setSaving(true);
    try {
      if (editing) {
        await apiClient.put(`/propriedades/${editing.id}`, values);
        message.success('Propriedade atualizada com sucesso.');
      } else {
        await apiClient.post('/propriedades', values);
        message.success('Propriedade criada com sucesso.');
      }
      closeModal();
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao salvar propriedade.');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleAtivo = async (record: PropriedadeResponse) => {
    try {
      await apiClient.patch(`/propriedades/${record.id}`, { ativo: !record.ativo });
      message.success(record.ativo ? 'Propriedade desativada.' : 'Propriedade ativada.');
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao alterar status.');
    }
  };

  const clienteLabel = (id: number) => clientes.find((c) => c.value === id)?.label ?? `#${id}`;

  const columns: ColumnsType<PropriedadeResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    { title: 'Nome', dataIndex: 'nome', key: 'nome' },
    { title: 'Cliente', dataIndex: 'cliente_id', key: 'cliente_id', render: (id: number) => clienteLabel(id) },
    { title: 'Município', dataIndex: 'municipio', key: 'municipio' },
    { title: 'Estado', dataIndex: 'estado', key: 'estado', width: 80 },
    { title: 'Área (ha)', dataIndex: 'area_total', key: 'area_total', width: 110 },
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
            title={record.ativo ? 'Desativar esta propriedade?' : 'Ativar esta propriedade?'}
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
  if (filterCliente !== undefined) extraParams.cliente_id = filterCliente;
  if (filterAtivo !== undefined) extraParams.ativo = filterAtivo;

  return (
    <div>
      <Title level={2}>Propriedades</Title>
      <Text type="secondary">Gestão de propriedades rurais.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Select
          placeholder="Filtrar por cliente"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 220 }}
          options={clientes}
          onChange={(v) => setFilterCliente(v)}
        />
        <Select
          placeholder="Filtrar por status"
          allowClear
          style={{ width: 160 }}
          options={[{ value: true, label: 'Ativo' }, { value: false, label: 'Inativo' }]}
          onChange={(v) => setFilterAtivo(v)}
        />
      </Space>

      <DataTable<PropriedadeResponse>
        columns={columns}
        apiUrl="/propriedades"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Nova Propriedade
          </Button>
        }
      />

      <FormModal<PropriedadeCreate & PropriedadeUpdate>
        open={modalOpen}
        title={editing ? 'Editar Propriedade' : 'Nova Propriedade'}
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        width={700}
        initialValues={
          editing
            ? {
                cliente_id: editing.cliente_id,
                nome: editing.nome,
                municipio: editing.municipio,
                estado: editing.estado,
                area_total: editing.area_total,
                latitude: editing.latitude,
                longitude: editing.longitude,
              }
            : undefined
        }
      >
        <Form.Item name="cliente_id" label="Cliente" rules={[{ required: true, message: 'Selecione o cliente' }]}>
          <Select options={clientes} showSearch optionFilterProp="label" placeholder="Selecione" />
        </Form.Item>
        <Form.Item name="nome" label="Nome" rules={[{ required: true, message: 'Informe o nome' }]}>
          <Input maxLength={200} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="municipio" label="Município" rules={[{ required: true, message: 'Informe o município' }]}>
              <Input maxLength={120} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="estado" label="Estado" rules={[{ required: true, message: 'Selecione o estado' }]}>
              <Select allowClear placeholder="UF" options={ESTADOS.map((uf) => ({ value: uf, label: uf }))} />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item name="area_total" label="Área Total (ha)" rules={[{ required: true, message: 'Informe a área' }]}>
          <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="latitude" label="Latitude">
              <InputNumber min={-90} max={90} step={0.000001} precision={6} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="longitude" label="Longitude">
              <InputNumber min={-180} max={180} step={0.000001} precision={6} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>
      </FormModal>
    </div>
  );
}
