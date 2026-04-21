import { useCallback, useState } from 'react';
import { Button, Col, DatePicker, Form, Input, InputNumber, Row, Select, Space, Typography, message } from 'antd';
import { DownloadOutlined, UploadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { DocumentoOficialResponse } from '../types/documento-oficial';
import type { DocumentoEntidade, DocumentoStatus } from '../types/enums';

const { Title, Text } = Typography;

const ENTIDADE_OPTIONS: { value: DocumentoEntidade; label: string }[] = [
  { value: 'DRONE', label: 'Drone' },
  { value: 'MANUTENCAO', label: 'Manutenção' },
  { value: 'USUARIO', label: 'Usuário' },
  { value: 'CLIENTE', label: 'Cliente' },
  { value: 'PROPRIEDADE', label: 'Propriedade' },
  { value: 'INSUMO', label: 'Insumo' },
  { value: 'MISSAO', label: 'Missão' },
];

const STATUS_OPTIONS: { value: DocumentoStatus; label: string }[] = [
  { value: 'ATIVO', label: 'Ativo' },
  { value: 'SUBSTITUIDO', label: 'Substituído' },
  { value: 'VENCIDO', label: 'Vencido' },
  { value: 'INATIVO', label: 'Inativo' },
];

export default function Documentos() {
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Filters
  const [filterEntidade, setFilterEntidade] = useState<DocumentoEntidade | undefined>();
  const [filterEntidadeId, setFilterEntidadeId] = useState<number | undefined>();
  const [filterTipoDoc, setFilterTipoDoc] = useState<string | undefined>();
  const [filterStatus, setFilterStatus] = useState<DocumentoStatus | undefined>();

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  const openCreate = () => { setSelectedFile(null); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setSelectedFile(null); };

  const handleSubmit = async (values: Record<string, unknown>) => {
    if (!selectedFile) {
      message.warning('Selecione um arquivo para upload.');
      return;
    }
    setSaving(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('entidade', values.entidade);
      formData.append('entidade_id', String(values.entidade_id));
      formData.append('tipo_documento', values.tipo_documento);
      if (values.descricao) formData.append('descricao', values.descricao);
      if (values.data_emissao) formData.append('data_emissao', dayjs(values.data_emissao).format('YYYY-MM-DD'));
      if (values.data_validade) formData.append('data_validade', dayjs(values.data_validade).format('YYYY-MM-DD'));

      await apiClient.post('/documentos-oficiais', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      message.success('Documento enviado com sucesso.');
      closeModal();
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao enviar documento.');
    } finally {
      setSaving(false);
    }
  };

  const handleDownload = async (id: number) => {
    try {
      const { data } = await apiClient.get<{ url: string; expires_in: number }>(
        `/documentos-oficiais/${id}/download`,
      );
      window.open(data.url, '_blank');
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao baixar documento.');
    }
  };

  const columns: ColumnsType<DocumentoOficialResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    { title: 'Entidade', dataIndex: 'entidade', key: 'entidade', width: 130 },
    { title: 'Entidade ID', dataIndex: 'entidade_id', key: 'entidade_id', width: 110 },
    { title: 'Tipo Documento', dataIndex: 'tipo_documento', key: 'tipo_documento', width: 160 },
    { title: 'Descrição', dataIndex: 'descricao', key: 'descricao', ellipsis: true, render: (v: string | null) => v || '—' },
    { title: 'Nome Arquivo', dataIndex: 'nome_arquivo', key: 'nome_arquivo', ellipsis: true },
    {
      title: 'Status', dataIndex: 'status', key: 'status', width: 120,
      render: (s: DocumentoStatus) => <StatusBadge status={s} />,
    },
    {
      title: 'Data Emissão', dataIndex: 'data_emissao', key: 'data_emissao', width: 130,
      render: (d: string | null) => d ? dayjs(d).format('DD/MM/YYYY') : '—',
    },
    {
      title: 'Data Validade', dataIndex: 'data_validade', key: 'data_validade', width: 130,
      render: (d: string | null) => d ? dayjs(d).format('DD/MM/YYYY') : '—',
    },
    {
      title: 'Ações', key: 'acoes', width: 120,
      render: (_, record) => (
        <Button
          size="small"
          icon={<DownloadOutlined />}
          onClick={() => handleDownload(record.id)}
        >
          Download
        </Button>
      ),
    },
  ];

  const extraParams: Record<string, unknown> = {};
  if (filterEntidade) extraParams.entidade = filterEntidade;
  if (filterEntidadeId) extraParams.entidade_id = filterEntidadeId;
  if (filterTipoDoc) extraParams.tipo_documento = filterTipoDoc;
  if (filterStatus) extraParams.status = filterStatus;

  return (
    <div>
      <Title level={2}>Documentos Oficiais</Title>
      <Text type="secondary">Gestão de documentos regulatórios.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Select
          placeholder="Entidade"
          allowClear
          style={{ width: 160 }}
          options={ENTIDADE_OPTIONS}
          onChange={(v) => setFilterEntidade(v)}
        />
        <InputNumber
          placeholder="Entidade ID"
          style={{ width: 130 }}
          min={1}
          onChange={(v) => setFilterEntidadeId(v ?? undefined)}
        />
        <Input
          placeholder="Tipo Documento"
          allowClear
          style={{ width: 180 }}
          onChange={(e) => setFilterTipoDoc(e.target.value || undefined)}
        />
        <Select
          placeholder="Status"
          allowClear
          style={{ width: 150 }}
          options={STATUS_OPTIONS}
          onChange={(v) => setFilterStatus(v)}
        />
      </Space>

      <DataTable<DocumentoOficialResponse>
        columns={columns}
        apiUrl="/documentos-oficiais"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<UploadOutlined />} onClick={openCreate}>
            Novo Documento
          </Button>
        }
      />

      <FormModal
        open={modalOpen}
        title="Upload de Documento"
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        width={650}
      >
        <Form.Item
          label="Arquivo"
          required
          help={selectedFile ? selectedFile.name : undefined}
        >
          <input
            type="file"
            onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
          />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="entidade"
              label="Entidade"
              rules={[{ required: true, message: 'Selecione a entidade' }]}
            >
              <Select options={ENTIDADE_OPTIONS} placeholder="Selecione" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="entidade_id"
              label="Entidade ID"
              rules={[{ required: true, message: 'Informe o ID da entidade' }]}
            >
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item
          name="tipo_documento"
          label="Tipo Documento"
          rules={[{ required: true, message: 'Informe o tipo do documento' }]}
        >
          <Input maxLength={120} />
        </Form.Item>
        <Form.Item name="descricao" label="Descrição">
          <Input.TextArea rows={2} maxLength={2000} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="data_emissao" label="Data Emissão">
              <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="data_validade" label="Data Validade">
              <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
        </Row>
      </FormModal>
    </div>
  );
}
