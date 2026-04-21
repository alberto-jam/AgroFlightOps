import { useCallback, useState } from 'react';
import { Button, Col, DatePicker, Form, Input, InputNumber, message, Popconfirm, Row, Select, Space, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { InsumoResponse, InsumoCreate, InsumoUpdate } from '../types/insumo';

const { Title, Text } = Typography;

export default function Insumos() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<InsumoResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [filterNome, setFilterNome] = useState<string | undefined>();
  const [filterAtivo, setFilterAtivo] = useState<boolean | undefined>();

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (record: InsumoResponse) => { setEditing(record); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); };

  const handleSubmit = async (values: Record<string, unknown>) => {
    setSaving(true);
    try {
      const payload = { ...values };
      if (payload.validade) {
        payload.validade = dayjs(payload.validade).format('YYYY-MM-DD');
      } else {
        payload.validade = null;
      }
      if (editing) {
        await apiClient.put(`/insumos/${editing.id}`, payload);
        message.success('Insumo atualizado com sucesso.');
      } else {
        await apiClient.post('/insumos', payload);
        message.success('Insumo criado com sucesso.');
      }
      closeModal();
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao salvar insumo.');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleAtivo = async (record: InsumoResponse) => {
    try {
      await apiClient.patch(`/insumos/${record.id}`, { ativo: !record.ativo });
      message.success(record.ativo ? 'Insumo desativado.' : 'Insumo ativado.');
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao alterar status.');
    }
  };

  const columns: ColumnsType<InsumoResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    { title: 'Nome', dataIndex: 'nome', key: 'nome' },
    { title: 'Fabricante', dataIndex: 'fabricante', key: 'fabricante', render: (v: string | null) => v || '—' },
    { title: 'Unidade', dataIndex: 'unidade_medida', key: 'unidade_medida', width: 100 },
    { title: 'Saldo', dataIndex: 'saldo_atual', key: 'saldo_atual', width: 100 },
    { title: 'Lote', dataIndex: 'lote', key: 'lote', render: (v: string | null) => v || '—' },
    {
      title: 'Validade', dataIndex: 'validade', key: 'validade', width: 120,
      render: (v: string | null) => v ? dayjs(v).format('DD/MM/YYYY') : '—',
    },
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
            title={record.ativo ? 'Desativar este insumo?' : 'Ativar este insumo?'}
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
  if (filterNome) extraParams.nome = filterNome;
  if (filterAtivo !== undefined) extraParams.ativo = filterAtivo;

  return (
    <div>
      <Title level={2}>Insumos</Title>
      <Text type="secondary">Gestão de insumos e estoque.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Input.Search
          placeholder="Filtrar por nome"
          allowClear
          style={{ width: 240 }}
          onSearch={(v) => setFilterNome(v || undefined)}
        />
        <Select
          placeholder="Filtrar por status"
          allowClear
          style={{ width: 160 }}
          options={[{ value: true, label: 'Ativo' }, { value: false, label: 'Inativo' }]}
          onChange={(v) => setFilterAtivo(v)}
        />
      </Space>

      <DataTable<InsumoResponse>
        columns={columns}
        apiUrl="/insumos"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Novo Insumo
          </Button>
        }
      />

      <FormModal<InsumoCreate & InsumoUpdate>
        open={modalOpen}
        title={editing ? 'Editar Insumo' : 'Novo Insumo'}
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        initialValues={
          editing
            ? {
                nome: editing.nome,
                fabricante: editing.fabricante,
                unidade_medida: editing.unidade_medida,
                saldo_atual: editing.saldo_atual,
                lote: editing.lote,
                validade: editing.validade ? dayjs(editing.validade) : undefined,
              } as any
            : undefined
        }
      >
        <Form.Item name="nome" label="Nome" rules={[{ required: true, message: 'Informe o nome' }]}>
          <Input maxLength={200} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="fabricante" label="Fabricante">
              <Input maxLength={120} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="unidade_medida" label="Unidade de Medida" rules={[{ required: true, message: 'Informe a unidade' }]}>
              <Input maxLength={30} placeholder="L, kg, mL..." />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={8}>
            <Form.Item name="saldo_atual" label="Saldo Atual">
              <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="lote" label="Lote">
              <Input maxLength={100} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="validade" label="Validade">
              <DatePicker format="DD/MM/YYYY" style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>
      </FormModal>
    </div>
  );
}
