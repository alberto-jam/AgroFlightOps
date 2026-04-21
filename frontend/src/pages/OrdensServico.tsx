import { useCallback, useEffect, useState } from 'react';
import {
  Button, Col, DatePicker, Dropdown, Form, Input, message, Modal,
  Row, Select, Space, Table, Tag, Typography,
} from 'antd';
import {
  DownOutlined, ExclamationCircleOutlined, HistoryOutlined, PlusOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { MenuProps } from 'antd';
import dayjs from 'dayjs';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type {
  OrdemServicoResponse,
  OrdemServicoUpdate,
  HistoricoStatusOSResponse,
} from '../types/ordem-servico';
import type { OrdemServicoStatus, Prioridade } from '../types/enums';
import type { ClienteResponse } from '../types/cliente';
import type { PropriedadeResponse } from '../types/propriedade';
import type { TalhaoResponse } from '../types/talhao';
import type { CulturaResponse } from '../types/cultura';

const { Title, Text } = Typography;

const STATUS_OPTIONS: { value: OrdemServicoStatus; label: string }[] = [
  { value: 'RASCUNHO', label: 'Rascunho' },
  { value: 'EM_ANALISE', label: 'Em Análise' },
  { value: 'APROVADA', label: 'Aprovada' },
  { value: 'REJEITADA', label: 'Rejeitada' },
  { value: 'CANCELADA', label: 'Cancelada' },
];

const PRIORIDADE_OPTIONS: { value: Prioridade; label: string }[] = [
  { value: 'BAIXA', label: 'Baixa' },
  { value: 'MEDIA', label: 'Média' },
  { value: 'ALTA', label: 'Alta' },
  { value: 'CRITICA', label: 'Crítica' },
];

/** Allowed transitions per current status. */
const TRANSITIONS: Record<OrdemServicoStatus, { label: string; target: OrdemServicoStatus }[]> = {
  RASCUNHO: [
    { label: 'Submeter', target: 'EM_ANALISE' },
    { label: 'Cancelar', target: 'CANCELADA' },
  ],
  EM_ANALISE: [
    { label: 'Aprovar', target: 'APROVADA' },
    { label: 'Rejeitar', target: 'REJEITADA' },
    { label: 'Cancelar', target: 'CANCELADA' },
  ],
  APROVADA: [
    { label: 'Cancelar', target: 'CANCELADA' },
  ],
  REJEITADA: [],
  CANCELADA: [],
};

type DropdownOption = { value: number; label: string };

export default function OrdensServico() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<OrdemServicoResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Filters
  const [filterStatus, setFilterStatus] = useState<OrdemServicoStatus | undefined>();
  const [filterCliente, setFilterCliente] = useState<number | undefined>();
  const [filterPropriedade, setFilterPropriedade] = useState<number | undefined>();
  const [filterPrioridade, setFilterPrioridade] = useState<Prioridade | undefined>();
  const [filterData, setFilterData] = useState<string | undefined>();

  // Dropdown data
  const [clientes, setClientes] = useState<DropdownOption[]>([]);
  const [propriedades, setPropriedades] = useState<DropdownOption[]>([]);
  const [, setTalhoes] = useState<DropdownOption[]>([]);
  const [culturas, setCulturas] = useState<DropdownOption[]>([]);

  // Form-specific cascading state
  const [formClienteId, setFormClienteId] = useState<number | undefined>();
  const [formPropriedadeId, setFormPropriedadeId] = useState<number | undefined>();
  const [formPropriedades, setFormPropriedades] = useState<DropdownOption[]>([]);
  const [formTalhoes, setFormTalhoes] = useState<DropdownOption[]>([]);

  // Transition modal
  const [transModal, setTransModal] = useState<{
    os: OrdemServicoResponse;
    target: OrdemServicoStatus;
    label: string;
  } | null>(null);
  const [transMotivo, setTransMotivo] = useState('');
  const [transLoading, setTransLoading] = useState(false);

  // History modal
  const [historyOs, setHistoryOs] = useState<OrdemServicoResponse | null>(null);
  const [history, setHistory] = useState<HistoricoStatusOSResponse[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  // Load dropdown data
  useEffect(() => {
    apiClient.get<{ items: ClienteResponse[] }>('/clientes', { params: { page_size: 100 } })
      .then(({ data }) => setClientes(data.items.map((c) => ({ value: c.id, label: c.nome }))));
    apiClient.get<{ items: PropriedadeResponse[] }>('/propriedades', { params: { page_size: 100 } })
      .then(({ data }) => setPropriedades(data.items.map((p) => ({ value: p.id, label: p.nome }))));
    apiClient.get<{ items: TalhaoResponse[] }>('/talhoes', { params: { page_size: 100 } })
      .then(({ data }) => setTalhoes(data.items.map((t) => ({ value: t.id, label: t.nome }))));
    apiClient.get<{ items: CulturaResponse[] }>('/culturas', { params: { page_size: 100 } })
      .then(({ data }) => setCulturas(data.items.map((c) => ({ value: c.id, label: c.nome }))));
  }, []);

  // Cascade: when formClienteId changes, filter propriedades
  useEffect(() => {
    if (!formClienteId) { setFormPropriedades([]); setFormTalhoes([]); return; }
    apiClient.get<{ items: PropriedadeResponse[] }>('/propriedades', {
      params: { page_size: 100, cliente_id: formClienteId },
    }).then(({ data }) =>
      setFormPropriedades(data.items.map((p) => ({ value: p.id, label: p.nome }))),
    );
    setFormPropriedadeId(undefined);
    setFormTalhoes([]);
  }, [formClienteId]);

  // Cascade: when formPropriedadeId changes, filter talhões
  useEffect(() => {
    if (!formPropriedadeId) { setFormTalhoes([]); return; }
    apiClient.get<{ items: TalhaoResponse[] }>('/talhoes', {
      params: { page_size: 100, propriedade_id: formPropriedadeId },
    }).then(({ data }) =>
      setFormTalhoes(data.items.map((t) => ({ value: t.id, label: t.nome }))),
    );
  }, [formPropriedadeId]);

  const lookupLabel = (list: DropdownOption[], id: number) =>
    list.find((o) => o.value === id)?.label ?? `#${id}`;

  // CRUD handlers
  const openCreate = () => {
    setEditing(null);
    setFormClienteId(undefined);
    setFormPropriedadeId(undefined);
    setModalOpen(true);
  };
  const openEdit = (record: OrdemServicoResponse) => {
    setEditing(record);
    setFormClienteId(record.cliente_id);
    setFormPropriedadeId(record.propriedade_id);
    setModalOpen(true);
  };
  const closeModal = () => { setModalOpen(false); setEditing(null); };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
const handleSubmit = async (values: any) => {
    setSaving(true);
    try {
      const payload = {
        ...values,
        data_prevista: values.data_prevista
          ? dayjs(values.data_prevista).format('YYYY-MM-DD')
          : undefined,
      };
      if (editing) {
        const updatePayload: OrdemServicoUpdate = {
          tipo_aplicacao: payload.tipo_aplicacao,
          prioridade: payload.prioridade,
          descricao: payload.descricao,
          data_prevista: payload.data_prevista,
        };
        await apiClient.put(`/ordens-servico/${editing.id}`, updatePayload);
        message.success('Ordem de Serviço atualizada.');
      } else {
        await apiClient.post('/ordens-servico', payload);
        message.success('Ordem de Serviço criada.');
      }
      closeModal();
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao salvar OS.');
    } finally {
      setSaving(false);
    }
  };

  // Status transition
  const openTransition = (os: OrdemServicoResponse, target: OrdemServicoStatus, label: string) => {
    setTransModal({ os, target, label });
    setTransMotivo('');
  };

  const handleTransition = async () => {
    if (!transModal) return;
    const needsMotivo = transModal.target === 'REJEITADA' || transModal.target === 'CANCELADA';
    if (needsMotivo && !transMotivo.trim()) {
      message.warning('Informe o motivo.');
      return;
    }
    setTransLoading(true);
    try {
      await apiClient.patch(`/ordens-servico/${transModal.os.id}/transicao`, {
        status_novo: transModal.target,
        motivo: transMotivo || undefined,
      });
      message.success(`OS ${transModal.label.toLowerCase()} com sucesso.`);
      setTransModal(null);
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro na transição de status.');
    } finally {
      setTransLoading(false);
    }
  };

  // History
  const openHistory = async (os: OrdemServicoResponse) => {
    setHistoryOs(os);
    setHistoryLoading(true);
    try {
      const { data } = await apiClient.get<HistoricoStatusOSResponse[]>(
        `/ordens-servico/${os.id}/historico`,
      );
      setHistory(data);
    } catch {
      message.error('Erro ao carregar histórico.');
    } finally {
      setHistoryLoading(false);
    }
  };

  const transitionMenu = (record: OrdemServicoResponse): MenuProps['items'] => {
    const items = TRANSITIONS[record.status] ?? [];
    if (!items.length) return [{ key: 'none', label: 'Sem transições', disabled: true }];
    return items.map((t) => ({
      key: t.target,
      label: t.label,
      danger: t.target === 'CANCELADA' || t.target === 'REJEITADA',
      onClick: () => openTransition(record, t.target, t.label),
    }));
  };

  const columns: ColumnsType<OrdemServicoResponse> = [
    { title: 'Código', dataIndex: 'codigo', key: 'codigo', width: 120 },
    {
      title: 'Cliente', dataIndex: 'cliente_id', key: 'cliente_id',
      render: (id: number) => lookupLabel(clientes, id),
    },
    {
      title: 'Propriedade', dataIndex: 'propriedade_id', key: 'propriedade_id',
      render: (id: number) => lookupLabel(propriedades, id),
    },
    {
      title: 'Prioridade', dataIndex: 'prioridade', key: 'prioridade', width: 110,
      render: (p: Prioridade) => <StatusBadge status={p} />,
    },
    { title: 'Data Prevista', dataIndex: 'data_prevista', key: 'data_prevista', width: 120 },
    {
      title: 'Status', dataIndex: 'status', key: 'status', width: 130,
      render: (s: OrdemServicoStatus) => <StatusBadge status={s} />,
    },
    {
      title: 'Ações', key: 'acoes', width: 280,
      render: (_, record) => (
        <Space>
          {(record.status === 'RASCUNHO') && (
            <Button size="small" onClick={() => openEdit(record)}>Editar</Button>
          )}
          <Dropdown menu={{ items: transitionMenu(record) }}>
            <Button size="small">
              Ações <DownOutlined />
            </Button>
          </Dropdown>
          <Button
            size="small"
            icon={<HistoryOutlined />}
            onClick={() => openHistory(record)}
          >
            Histórico
          </Button>
        </Space>
      ),
    },
  ];

  const extraParams: Record<string, unknown> = {};
  if (filterStatus) extraParams.status = filterStatus;
  if (filterCliente) extraParams.cliente_id = filterCliente;
  if (filterPropriedade) extraParams.propriedade_id = filterPropriedade;
  if (filterPrioridade) extraParams.prioridade = filterPrioridade;
  if (filterData) extraParams.data_prevista = filterData;

  const needsMotivo = transModal?.target === 'REJEITADA' || transModal?.target === 'CANCELADA';

  const historyColumns: ColumnsType<HistoricoStatusOSResponse> = [
    {
      title: 'De', dataIndex: 'status_anterior', key: 'status_anterior', width: 140,
      render: (s: string | null) => s ? <StatusBadge status={s} /> : <Tag>—</Tag>,
    },
    {
      title: 'Para', dataIndex: 'status_novo', key: 'status_novo', width: 140,
      render: (s: string) => <StatusBadge status={s} />,
    },
    { title: 'Motivo', dataIndex: 'motivo', key: 'motivo', render: (v: string | null) => v || '—' },
    {
      title: 'Data', dataIndex: 'created_at', key: 'created_at', width: 170,
      render: (d: string) => dayjs(d).format('DD/MM/YYYY HH:mm'),
    },
  ];

  return (
    <div>
      <Title level={2}>Ordens de Serviço</Title>
      <Text type="secondary">Gestão de ordens de serviço de pulverização.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Select
          placeholder="Status"
          allowClear
          style={{ width: 160 }}
          options={STATUS_OPTIONS}
          onChange={(v) => setFilterStatus(v)}
        />
        <Select
          placeholder="Cliente"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 200 }}
          options={clientes}
          onChange={(v) => setFilterCliente(v)}
        />
        <Select
          placeholder="Propriedade"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 200 }}
          options={propriedades}
          onChange={(v) => setFilterPropriedade(v)}
        />
        <Select
          placeholder="Prioridade"
          allowClear
          style={{ width: 150 }}
          options={PRIORIDADE_OPTIONS}
          onChange={(v) => setFilterPrioridade(v)}
        />
        <DatePicker
          placeholder="Data Prevista"
          onChange={(d) => setFilterData(d ? d.format('YYYY-MM-DD') : undefined)}
          format="DD/MM/YYYY"
        />
      </Space>

      <DataTable<OrdemServicoResponse>
        columns={columns}
        apiUrl="/ordens-servico"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Nova OS
          </Button>
        }
      />

      {/* Create / Edit Modal */}
      <FormModal
        open={modalOpen}
        title={editing ? 'Editar Ordem de Serviço' : 'Nova Ordem de Serviço'}
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        width={700}
        initialValues={
          editing
            ? {
                cliente_id: editing.cliente_id,
                propriedade_id: editing.propriedade_id,
                talhao_id: editing.talhao_id,
                cultura_id: editing.cultura_id,
                tipo_aplicacao: editing.tipo_aplicacao,
                prioridade: editing.prioridade,
                descricao: editing.descricao,
                data_prevista: editing.data_prevista ? dayjs(editing.data_prevista) : undefined,
              }
            : undefined
        }
      >
        {!editing && (
          <Form.Item
            name="cliente_id"
            label="Cliente"
            rules={[{ required: true, message: 'Selecione o cliente' }]}
          >
            <Select
              options={clientes}
              showSearch
              optionFilterProp="label"
              placeholder="Selecione"
              onChange={(v) => setFormClienteId(v)}
            />
          </Form.Item>
        )}
        {!editing && (
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="propriedade_id"
                label="Propriedade"
                rules={[{ required: true, message: 'Selecione a propriedade' }]}
              >
                <Select
                  options={formPropriedades}
                  showSearch
                  optionFilterProp="label"
                  placeholder={formClienteId ? 'Selecione' : 'Selecione o cliente primeiro'}
                  disabled={!formClienteId}
                  onChange={(v) => setFormPropriedadeId(v)}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="talhao_id"
                label="Talhão"
                rules={[{ required: true, message: 'Selecione o talhão' }]}
              >
                <Select
                  options={formTalhoes}
                  showSearch
                  optionFilterProp="label"
                  placeholder={formPropriedadeId ? 'Selecione' : 'Selecione a propriedade primeiro'}
                  disabled={!formPropriedadeId}
                />
              </Form.Item>
            </Col>
          </Row>
        )}
        {!editing && (
          <Form.Item
            name="cultura_id"
            label="Cultura"
            rules={[{ required: true, message: 'Selecione a cultura' }]}
          >
            <Select
              options={culturas}
              showSearch
              optionFilterProp="label"
              placeholder="Selecione"
            />
          </Form.Item>
        )}
        <Form.Item
          name="tipo_aplicacao"
          label="Tipo de Aplicação"
          rules={[{ required: true, message: 'Informe o tipo de aplicação' }]}
        >
          <Input maxLength={120} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="prioridade"
              label="Prioridade"
              rules={[{ required: true, message: 'Selecione a prioridade' }]}
            >
              <Select options={PRIORIDADE_OPTIONS} placeholder="Selecione" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="data_prevista"
              label="Data Prevista"
              rules={[{ required: true, message: 'Informe a data prevista' }]}
            >
              <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item name="descricao" label="Observações">
          <Input.TextArea rows={3} maxLength={2000} />
        </Form.Item>
      </FormModal>

      {/* Transition Confirmation Modal */}
      <Modal
        open={!!transModal}
        title={
          <Space>
            <ExclamationCircleOutlined style={{ color: '#faad14' }} />
            {`Confirmar: ${transModal?.label}`}
          </Space>
        }
        onCancel={() => setTransModal(null)}
        onOk={handleTransition}
        confirmLoading={transLoading}
        okText="Confirmar"
        cancelText="Cancelar"
        okButtonProps={
          needsMotivo ? { danger: true } : undefined
        }
      >
        <p>
          Deseja {transModal?.label.toLowerCase()} a OS{' '}
          <strong>{transModal?.os.codigo}</strong>?
        </p>
        {needsMotivo && (
          <Form.Item
            label={transModal?.target === 'REJEITADA' ? 'Motivo da Rejeição' : 'Motivo do Cancelamento'}
            required
          >
            <Input.TextArea
              rows={3}
              value={transMotivo}
              onChange={(e) => setTransMotivo(e.target.value)}
              placeholder="Informe o motivo (obrigatório)"
            />
          </Form.Item>
        )}
      </Modal>

      {/* History Modal */}
      <Modal
        open={!!historyOs}
        title={`Histórico — ${historyOs?.codigo ?? ''}`}
        onCancel={() => setHistoryOs(null)}
        footer={null}
        width={700}
      >
        <Table<HistoricoStatusOSResponse>
          columns={historyColumns}
          dataSource={history}
          rowKey="id"
          loading={historyLoading}
          pagination={false}
          size="small"
        />
      </Modal>
    </div>
  );
}
