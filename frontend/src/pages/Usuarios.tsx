import { useCallback, useState } from 'react';
import { Button, Form, Input, message, Popconfirm, Select, Space, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { UsuarioResponse, UsuarioCreate, UsuarioUpdate } from '../types/usuario';

const { Title, Text } = Typography;

const PERFIL_OPTIONS = [
  { value: 1, label: 'Administrador' },
  { value: 2, label: 'Coordenador Operacional' },
  { value: 3, label: 'Piloto' },
  { value: 4, label: 'Técnico' },
  { value: 5, label: 'Financeiro' },
];

const perfilLabel = (id: number) =>
  PERFIL_OPTIONS.find((p) => p.value === id)?.label ?? `Perfil ${id}`;

export default function Usuarios() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<UsuarioResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [filterPerfil, setFilterPerfil] = useState<number | undefined>();
  const [filterAtivo, setFilterAtivo] = useState<boolean | undefined>();

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (record: UsuarioResponse) => { setEditing(record); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); };

  const handleSubmit = async (values: UsuarioCreate & UsuarioUpdate) => {
    setSaving(true);
    try {
      if (editing) {
        await apiClient.put(`/usuarios/${editing.id}`, values);
        message.success('Usuário atualizado com sucesso.');
      } else {
        await apiClient.post('/usuarios', values);
        message.success('Usuário criado com sucesso.');
      }
      closeModal();
      refresh();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      message.error(detail || 'Erro ao salvar usuário.');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleAtivo = async (record: UsuarioResponse) => {
    try {
      await apiClient.patch(`/usuarios/${record.id}`, { ativo: !record.ativo });
      message.success(record.ativo ? 'Usuário desativado.' : 'Usuário ativado.');
      refresh();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      message.error(detail || 'Erro ao alterar status do usuário.');
    }
  };

  const columns: ColumnsType<UsuarioResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    { title: 'Nome', dataIndex: 'nome', key: 'nome' },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    {
      title: 'Perfil', dataIndex: 'perfil_id', key: 'perfil_id',
      render: (id: number) => perfilLabel(id),
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
            title={record.ativo ? 'Desativar este usuário?' : 'Ativar este usuário?'}
            onConfirm={() => handleToggleAtivo(record)}
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
  if (filterPerfil !== undefined) extraParams.perfil_id = filterPerfil;
  if (filterAtivo !== undefined) extraParams.ativo = filterAtivo;

  return (
    <div>
      <Title level={2}>Usuários</Title>
      <Text type="secondary">Gestão de usuários do sistema.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Select
          placeholder="Filtrar por perfil"
          allowClear
          style={{ width: 200 }}
          options={PERFIL_OPTIONS}
          onChange={(v) => setFilterPerfil(v)}
        />
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

      <DataTable<UsuarioResponse>
        columns={columns}
        apiUrl="/usuarios"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Novo Usuário
          </Button>
        }
      />

      <FormModal<UsuarioCreate & UsuarioUpdate>
        open={modalOpen}
        title={editing ? 'Editar Usuário' : 'Novo Usuário'}
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        initialValues={
          editing
            ? { nome: editing.nome, email: editing.email, perfil_id: editing.perfil_id }
            : undefined
        }
      >
        <Form.Item name="nome" label="Nome" rules={[{ required: true, message: 'Informe o nome' }]}>
          <Input maxLength={200} />
        </Form.Item>
        <Form.Item
          name="email"
          label="Email"
          rules={[
            { required: true, message: 'Informe o email' },
            { type: 'email', message: 'Email inválido' },
          ]}
        >
          <Input maxLength={255} />
        </Form.Item>
        <Form.Item name="perfil_id" label="Perfil" rules={[{ required: true, message: 'Selecione o perfil' }]}>
          <Select options={PERFIL_OPTIONS} placeholder="Selecione" />
        </Form.Item>
        {!editing && (
          <Form.Item
            name="senha"
            label="Senha"
            rules={[
              { required: true, message: 'Informe a senha' },
              { min: 6, message: 'Mínimo 6 caracteres' },
            ]}
          >
            <Input.Password />
          </Form.Item>
        )}
      </FormModal>
    </div>
  );
}
