import { useCallback, useState } from 'react';
import { Button, Form, Input, message, Popconfirm, Select, Space, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { CulturaResponse, CulturaCreate, CulturaUpdate } from '../types/cultura';

const { Title, Text } = Typography;

export default function Culturas() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<CulturaResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [filterAtivo, setFilterAtivo] = useState<boolean | undefined>();

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (record: CulturaResponse) => { setEditing(record); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); };

  const handleSubmit = async (values: CulturaCreate & CulturaUpdate) => {
    setSaving(true);
    try {
      if (editing) {
        await apiClient.put(`/culturas/${editing.id}`, values);
        message.success('Cultura atualizada com sucesso.');
      } else {
        await apiClient.post('/culturas', values);
        message.success('Cultura criada com sucesso.');
      }
      closeModal();
      refresh();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao salvar cultura.');
    } finally {
      setSaving(false);
    }
  };

  const handleDesativar = async (record: CulturaResponse) => {
    try {
      await apiClient.patch(`/culturas/${record.id}`, { ativo: !record.ativo });
      message.success(record.ativo ? 'Cultura desativada.' : 'Cultura ativada.');
      refresh();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao alterar status da cultura.');
    }
  };

  const columns: ColumnsType<CulturaResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    { title: 'Nome', dataIndex: 'nome', key: 'nome' },
    { title: 'Descrição', dataIndex: 'descricao', key: 'descricao', render: (v: string | null) => v || '—' },
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
            title={record.ativo ? 'Desativar esta cultura?' : 'Ativar esta cultura?'}
            onConfirm={() => handleDesativar(record)}
            okText="Sim"
            cancelText="Não"
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
      <Title level={2}>Culturas</Title>
      <Text type="secondary">Gestão de tipos de cultura agrícola.</Text>

      <Space style={{ margin: '16px 0' }}>
        <Select
          placeholder="Filtrar por status"
          allowClear
          style={{ width: 160 }}
          options={[
            { value: true, label: 'Ativo' },
            { value: false, label: 'Inativo' },
          ]}
          onChange={(v) => setFilterAtivo(v)}
        />
      </Space>

      <DataTable<CulturaResponse>
        columns={columns}
        apiUrl="/culturas"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Nova Cultura
          </Button>
        }
      />

      <FormModal<CulturaCreate & CulturaUpdate>
        open={modalOpen}
        title={editing ? 'Editar Cultura' : 'Nova Cultura'}
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        initialValues={
          editing
            ? { nome: editing.nome, descricao: editing.descricao }
            : undefined
        }
      >
        <Form.Item name="nome" label="Nome" rules={[{ required: true, message: 'Informe o nome' }]}>
          <Input maxLength={120} />
        </Form.Item>
        <Form.Item name="descricao" label="Descrição">
          <Input.TextArea rows={3} />
        </Form.Item>
      </FormModal>
    </div>
  );
}
