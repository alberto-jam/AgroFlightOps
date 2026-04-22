import { useCallback, useState } from 'react';
import { Button, Col, Form, Input, InputNumber, message, Popconfirm, Row, Select, Space, Switch, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type {
  ItemChecklistPadraoResponse, ItemChecklistPadraoCreate, ItemChecklistPadraoUpdate,
} from '../types/checklist-padrao';

const { Title, Text } = Typography;

export default function ItensChecklistPadrao() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<ItemChecklistPadraoResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [filterAtivo, setFilterAtivo] = useState<boolean | undefined>();

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);
  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (record: ItemChecklistPadraoResponse) => { setEditing(record); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); };

  const handleSubmit = async (values: ItemChecklistPadraoCreate & ItemChecklistPadraoUpdate) => {
    setSaving(true);
    try {
      if (editing) {
        await apiClient.put(`/itens-checklist-padrao/${editing.id}`, values);
        message.success('Item atualizado.');
      } else {
        await apiClient.post('/itens-checklist-padrao', values);
        message.success('Item criado.');
      }
      closeModal();
      refresh();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao salvar item.');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleAtivo = async (record: ItemChecklistPadraoResponse) => {
    try {
      await apiClient.patch(`/itens-checklist-padrao/${record.id}`, { ativo: !record.ativo });
      message.success(record.ativo ? 'Item desativado.' : 'Item ativado.');
      refresh();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao alterar status.');
    }
  };

  const columns: ColumnsType<ItemChecklistPadraoResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    { title: 'Nome', dataIndex: 'nome_item', key: 'nome_item' },
    { title: 'Descrição', dataIndex: 'descricao', key: 'descricao', render: (v: string | null) => v || '—' },
    { title: 'Obrigatório', dataIndex: 'obrigatorio', key: 'obrigatorio', width: 110, render: (v: boolean) => v ? 'Sim' : 'Não' },
    { title: 'Ordem', dataIndex: 'ordem_exibicao', key: 'ordem_exibicao', width: 90 },
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
            title={record.ativo ? 'Desativar este item?' : 'Ativar este item?'}
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
  if (filterAtivo !== undefined) extraParams.ativo = filterAtivo;

  return (
    <div>
      <Title level={2}>Itens de Checklist Padrão</Title>
      <Text type="secondary">Gestão dos itens padrão do checklist pré-voo.</Text>

      <Space style={{ margin: '16px 0' }}>
        <Select
          placeholder="Filtrar por status"
          allowClear
          style={{ width: 160 }}
          options={[{ value: true, label: 'Ativo' }, { value: false, label: 'Inativo' }]}
          onChange={(v) => setFilterAtivo(v)}
        />
      </Space>

      <DataTable<ItemChecklistPadraoResponse>
        columns={columns}
        apiUrl="/itens-checklist-padrao"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Novo Item
          </Button>
        }
      />

      <FormModal<ItemChecklistPadraoCreate & ItemChecklistPadraoUpdate>
        open={modalOpen}
        title={editing ? 'Editar Item de Checklist' : 'Novo Item de Checklist'}
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        initialValues={
          editing
            ? {
                nome_item: editing.nome_item,
                descricao: editing.descricao,
                obrigatorio: editing.obrigatorio,
                ordem_exibicao: editing.ordem_exibicao,
              }
            : { obrigatorio: true, ordem_exibicao: 0 }
        }
      >
        <Form.Item name="nome_item" label="Nome do Item" rules={[{ required: true, message: 'Informe o nome' }]}>
          <Input maxLength={200} />
        </Form.Item>
        <Form.Item name="descricao" label="Descrição">
          <Input.TextArea rows={3} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="obrigatorio" label="Obrigatório" valuePropName="checked">
              <Switch checkedChildren="Sim" unCheckedChildren="Não" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="ordem_exibicao" label="Ordem de Exibição">
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>
      </FormModal>
    </div>
  );
}
