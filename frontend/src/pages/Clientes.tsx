import { useCallback, useState } from 'react';
import { Button, Col, Descriptions, Form, Input, message, Modal, Popconfirm, Row, Select, Space, Typography } from 'antd';
import { EnvironmentOutlined, PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { ClienteResponse, ClienteCreate, ClienteUpdate } from '../types/cliente';

const { Title, Text } = Typography;

const ESTADOS = [
  'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS',
  'MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO',
];

export default function Clientes() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<ClienteResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [filterNome, setFilterNome] = useState<string | undefined>();
  const [filterAtivo, setFilterAtivo] = useState<boolean | undefined>();
  const [viewing, setViewing] = useState<ClienteResponse | null>(null);

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (record: ClienteResponse) => { setEditing(record); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); };

  const handleSubmit = async (values: ClienteCreate & ClienteUpdate) => {
    setSaving(true);
    try {
      if (editing) {
        await apiClient.put(`/clientes/${editing.id}`, values);
        message.success('Cliente atualizado com sucesso.');
      } else {
        await apiClient.post('/clientes', values);
        message.success('Cliente criado com sucesso.');
      }
      closeModal();
      refresh();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao salvar cliente.');
    } finally {
      setSaving(false);
    }
  };

  const handleDesativar = async (record: ClienteResponse) => {
    try {
      await apiClient.patch(`/clientes/${record.id}`, { ativo: !record.ativo });
      message.success(record.ativo ? 'Cliente desativado.' : 'Cliente ativado.');
      refresh();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao alterar status do cliente.');
    }
  };

  const columns: ColumnsType<ClienteResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    { title: 'Nome', dataIndex: 'nome', key: 'nome' },
    { title: 'CPF/CNPJ', dataIndex: 'cpf_cnpj', key: 'cpf_cnpj', render: (v: string | null) => v || '—' },
    { title: 'Telefone', dataIndex: 'telefone', key: 'telefone', render: (v: string | null) => v || '—' },
    { title: 'Município', dataIndex: 'municipio', key: 'municipio', render: (v: string | null) => v || '—' },
    { title: 'Estado', dataIndex: 'estado', key: 'estado', width: 80, render: (v: string | null) => v || '—' },
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
            title={record.ativo ? 'Desativar este cliente?' : 'Ativar este cliente?'}
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
  if (filterNome) extraParams.nome = filterNome;
  if (filterAtivo !== undefined) extraParams.ativo = filterAtivo;

  return (
    <div>
      <Title level={2}>Clientes</Title>
      <Text type="secondary">Gestão de clientes contratantes.</Text>

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
          options={[
            { value: true, label: 'Ativo' },
            { value: false, label: 'Inativo' },
          ]}
          onChange={(v) => setFilterAtivo(v)}
        />
      </Space>

      <DataTable<ClienteResponse>
        columns={columns}
        apiUrl="/clientes"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        onRowClick={(record) => setViewing(record)}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Novo Cliente
          </Button>
        }
      />

      <FormModal<ClienteCreate & ClienteUpdate>
        open={modalOpen}
        title={editing ? 'Editar Cliente' : 'Novo Cliente'}
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        width={700}
        initialValues={
          editing
            ? {
                nome: editing.nome,
                cpf_cnpj: editing.cpf_cnpj,
                telefone: editing.telefone,
                email: editing.email,
                endereco: editing.endereco,
                numero: editing.numero,
                complemento: editing.complemento,
                bairro: editing.bairro,
                municipio: editing.municipio,
                estado: editing.estado,
                cep: editing.cep,
                latitude: editing.latitude,
                longitude: editing.longitude,
                referencia_local: editing.referencia_local,
              }
            : undefined
        }
      >
        <Form.Item name="nome" label="Nome" rules={[{ required: true, message: 'Informe o nome' }]}>
          <Input maxLength={200} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="cpf_cnpj" label="CPF/CNPJ">
              <Input maxLength={18} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="telefone" label="Telefone">
              <Input maxLength={30} />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item name="email" label="Email" rules={[{ type: 'email', message: 'Email inválido' }]}>
          <Input maxLength={255} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={16}>
            <Form.Item name="endereco" label="Endereço">
              <Input maxLength={255} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="numero" label="Número">
              <Input maxLength={20} />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={8}>
            <Form.Item name="complemento" label="Complemento">
              <Input maxLength={120} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="bairro" label="Bairro">
              <Input maxLength={120} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="cep" label="CEP">
              <Input maxLength={12} />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="municipio" label="Município">
              <Input maxLength={120} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="estado" label="Estado">
              <Select
                allowClear
                placeholder="Selecione"
                options={ESTADOS.map((uf) => ({ value: uf, label: uf }))}
              />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="latitude" label="Latitude">
              <Input type="number" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="longitude" label="Longitude">
              <Input type="number" />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item name="referencia_local" label="Referência Local">
          <Input maxLength={255} />
        </Form.Item>
      </FormModal>

      {/* View Modal with Google Maps */}
      <Modal
        open={!!viewing}
        title={<Space><EnvironmentOutlined /> {viewing?.nome}</Space>}
        onCancel={() => setViewing(null)}
        footer={null}
        width={950}
      >
        {viewing && (
          <Row gutter={24}>
            <Col span={12}>
              <Descriptions column={1} size="small" bordered>
                <Descriptions.Item label="ID">{viewing.id}</Descriptions.Item>
                <Descriptions.Item label="Nome">{viewing.nome}</Descriptions.Item>
                <Descriptions.Item label="CPF/CNPJ">{viewing.cpf_cnpj || '—'}</Descriptions.Item>
                <Descriptions.Item label="Telefone">{viewing.telefone || '—'}</Descriptions.Item>
                <Descriptions.Item label="Email">{viewing.email || '—'}</Descriptions.Item>
                <Descriptions.Item label="Endereço">
                  {[viewing.endereco, viewing.numero].filter(Boolean).join(', ') || '—'}
                </Descriptions.Item>
                <Descriptions.Item label="Bairro">{viewing.bairro || '—'}</Descriptions.Item>
                <Descriptions.Item label="Município/UF">
                  {[viewing.municipio, viewing.estado].filter(Boolean).join(' - ') || '—'}
                </Descriptions.Item>
                <Descriptions.Item label="CEP">{viewing.cep || '—'}</Descriptions.Item>
                <Descriptions.Item label="Latitude">{viewing.latitude ?? '—'}</Descriptions.Item>
                <Descriptions.Item label="Longitude">{viewing.longitude ?? '—'}</Descriptions.Item>
                <Descriptions.Item label="Referência">{viewing.referencia_local || '—'}</Descriptions.Item>
                <Descriptions.Item label="Status">{viewing.ativo ? 'Ativo' : 'Inativo'}</Descriptions.Item>
              </Descriptions>
            </Col>
            <Col span={12}>
              {viewing.latitude && viewing.longitude ? (
                <iframe
                  title="Localização"
                  width="100%"
                  height="400"
                  style={{ border: 0, borderRadius: 8 }}
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                  src={`https://maps.google.com/maps?q=${viewing.latitude},${viewing.longitude}&z=15&output=embed`}
                />
              ) : (
                <div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f5f5f5', borderRadius: 8 }}>
                  <Text type="secondary">Coordenadas não informadas</Text>
                </div>
              )}
            </Col>
          </Row>
        )}
      </Modal>
    </div>
  );
}
