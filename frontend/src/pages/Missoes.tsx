import { useCallback, useEffect, useState } from 'react';
import {
  Button, Col, DatePicker, Divider, Dropdown, Form, Input, InputNumber, message, Modal,
  Row, Select, Space, Table, Tabs, Tag, TimePicker, Typography, Upload,
} from 'antd';
import {
  BulbOutlined, DownOutlined, ExclamationCircleOutlined,
  HistoryOutlined, PlusOutlined, RocketOutlined, ThunderboltOutlined, UploadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { MenuProps } from 'antd';
import dayjs from 'dayjs';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { MissaoResponse, MissaoCreate, HistoricoStatusMissaoResponse } from '../types/missao';
import type { MissaoStatus } from '../types/enums';
import type { OrdemServicoResponse } from '../types/ordem-servico';
import type { UsuarioResponse } from '../types/usuario';
import type { DroneResponse } from '../types/drone';
import type { BateriaResponse } from '../types/bateria';
import type { InsumoResponse } from '../types/insumo';
import type { MissaoBateriaResponse } from '../types/missao-bateria';
import type { ReservaInsumoResponse, ConsumoInsumoMissaoResponse } from '../types/reserva-insumo';
import type { EvidenciaResponse } from '../types/evidencia';

const { Title, Text } = Typography;

const STATUS_OPTIONS: { value: MissaoStatus; label: string }[] = [
  { value: 'RASCUNHO', label: 'Rascunho' },
  { value: 'PLANEJADA', label: 'Planejada' },
  { value: 'AGENDADA', label: 'Agendada' },
  { value: 'EM_CHECKLIST', label: 'Em Checklist' },
  { value: 'LIBERADA', label: 'Liberada' },
  { value: 'EM_EXECUCAO', label: 'Em Execução' },
  { value: 'PAUSADA', label: 'Pausada' },
  { value: 'CONCLUIDA', label: 'Concluída' },
  { value: 'CANCELADA', label: 'Cancelada' },
  { value: 'ENCERRADA_TECNICAMENTE', label: 'Encerrada Tecnicamente' },
  { value: 'ENCERRADA_FINANCEIRAMENTE', label: 'Encerrada Financeiramente' },
];

const TRANSITIONS: Record<MissaoStatus, { label: string; target: MissaoStatus }[]> = {
  RASCUNHO: [
    { label: 'Planejar', target: 'PLANEJADA' },
    { label: 'Cancelar', target: 'CANCELADA' },
  ],
  PLANEJADA: [
    { label: 'Agendar', target: 'AGENDADA' },
    { label: 'Cancelar', target: 'CANCELADA' },
  ],
  AGENDADA: [
    { label: 'Iniciar Checklist', target: 'EM_CHECKLIST' },
    { label: 'Cancelar', target: 'CANCELADA' },
  ],
  EM_CHECKLIST: [
    { label: 'Liberar', target: 'LIBERADA' },
  ],
  LIBERADA: [
    { label: 'Iniciar Execução', target: 'EM_EXECUCAO' },
  ],
  EM_EXECUCAO: [
    { label: 'Pausar', target: 'PAUSADA' },
    { label: 'Concluir', target: 'CONCLUIDA' },
  ],
  PAUSADA: [
    { label: 'Retomar Execução', target: 'EM_EXECUCAO' },
  ],
  CONCLUIDA: [
    { label: 'Encerrar Tecnicamente', target: 'ENCERRADA_TECNICAMENTE' },
  ],
  ENCERRADA_TECNICAMENTE: [
    { label: 'Encerrar Financeiramente', target: 'ENCERRADA_FINANCEIRAMENTE' },
  ],
  ENCERRADA_FINANCEIRAMENTE: [],
  CANCELADA: [],
};

type DropdownOption = { value: number; label: string };

export default function Missoes() {
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Filters
  const [filterStatus, setFilterStatus] = useState<MissaoStatus | undefined>();
  const [filterPiloto, setFilterPiloto] = useState<number | undefined>();
  const [filterDrone, setFilterDrone] = useState<number | undefined>();
  const [filterData, setFilterData] = useState<string | undefined>();
  const [filterOS, setFilterOS] = useState<number | undefined>();

  // Dropdown data
  const [ordensServico, setOrdensServico] = useState<DropdownOption[]>([]);
  const [pilotos, setPilotos] = useState<DropdownOption[]>([]);
  const [tecnicos, setTecnicos] = useState<DropdownOption[]>([]);
  const [drones, setDrones] = useState<DropdownOption[]>([]);
  const [baterias, setBaterias] = useState<DropdownOption[]>([]);
  const [insumos, setInsumos] = useState<DropdownOption[]>([]);

  // Transition modal
  const [transModal, setTransModal] = useState<{
    missao: MissaoResponse; target: MissaoStatus; label: string;
  } | null>(null);
  const [transMotivo, setTransMotivo] = useState('');
  const [transLoading, setTransLoading] = useState(false);

  // History modal
  const [historyMissao, setHistoryMissao] = useState<MissaoResponse | null>(null);
  const [history, setHistory] = useState<HistoricoStatusMissaoResponse[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Baterias modal
  const [batMissao, setBatMissao] = useState<MissaoResponse | null>(null);
  const [batList, setBatList] = useState<MissaoBateriaResponse[]>([]);
  const [batLoading, setBatLoading] = useState(false);
  const [batAdding, setBatAdding] = useState(false);
  const [batFormOpen, setBatFormOpen] = useState(false);

  // Reservas insumo modal
  const [resMissao, setResMissao] = useState<MissaoResponse | null>(null);
  const [resList, setResList] = useState<ReservaInsumoResponse[]>([]);
  const [resLoading, setResLoading] = useState(false);
  const [resAdding, setResAdding] = useState(false);
  const [resFormOpen, setResFormOpen] = useState(false);

  // Execution modal
  const [execMissao, setExecMissao] = useState<MissaoResponse | null>(null);
  const [execSaving, setExecSaving] = useState(false);
  const [execForm] = Form.useForm();
  const [consumosList, setConsumosList] = useState<ConsumoInsumoMissaoResponse[]>([]);
  const [consumosLoading, setConsumosLoading] = useState(false);
  const [consumoFormOpen, setConsumoFormOpen] = useState(false);
  const [consumoAdding, setConsumoAdding] = useState(false);
  const [evidenciasList, setEvidenciasList] = useState<EvidenciaResponse[]>([]);
  const [evidenciasLoading, setEvidenciasLoading] = useState(false);
  const [evidUploading, setEvidUploading] = useState(false);
  const [evidLat, setEvidLat] = useState<number | null>(null);
  const [evidLng, setEvidLng] = useState<number | null>(null);

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  // Load dropdown data
  useEffect(() => {
    apiClient.get<{ items: OrdemServicoResponse[] }>('/ordens-servico', {
      params: { page_size: 200, status: 'APROVADA' },
    }).then(({ data }) =>
      setOrdensServico(data.items.map((o) => ({ value: o.id, label: o.codigo }))),
    );
    apiClient.get<{ items: UsuarioResponse[] }>('/usuarios', { params: { page_size: 200 } })
      .then(({ data }) => {
        const all = data.items.map((u) => ({ value: u.id, label: u.nome }));
        setPilotos(all);
        setTecnicos(all);
      });
    apiClient.get<{ items: DroneResponse[] }>('/drones', { params: { page_size: 200 } })
      .then(({ data }) =>
        setDrones(data.items.map((d) => ({ value: d.id, label: d.identificacao }))),
      );
    apiClient.get<{ items: BateriaResponse[] }>('/baterias', { params: { page_size: 200 } })
      .then(({ data }) =>
        setBaterias(data.items.map((b) => ({ value: b.id, label: b.identificacao }))),
      );
    apiClient.get<{ items: InsumoResponse[] }>('/insumos', { params: { page_size: 200 } })
      .then(({ data }) =>
        setInsumos(data.items.map((i) => ({ value: i.id, label: `${i.nome} (${i.unidade_medida})` }))),
      );
  }, []);

  const lookupLabel = (list: DropdownOption[], id: number) =>
    list.find((o) => o.value === id)?.label ?? `#${id}`;

  // CRUD
  const openCreate = () => setModalOpen(true);
  const closeModal = () => setModalOpen(false);

  const handleSubmit = async (values: Record<string, unknown>) => {
    setSaving(true);
    try {
      const payload: MissaoCreate = {
        ...values,
        data_agendada: dayjs(values.data_agendada).format('YYYY-MM-DD'),
        hora_agendada: dayjs(values.hora_agendada).format('HH:mm:ss'),
      };
      await apiClient.post('/missoes', payload);
      message.success('Missão criada.');
      closeModal();
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao criar missão.');
    } finally {
      setSaving(false);
    }
  };

  // Transitions
  const openTransition = (missao: MissaoResponse, target: MissaoStatus, label: string) => {
    setTransModal({ missao, target, label });
    setTransMotivo('');
  };

  const handleTransition = async () => {
    if (!transModal) return;
    if (transModal.target === 'CANCELADA' && !transMotivo.trim()) {
      message.warning('Informe o motivo do cancelamento.');
      return;
    }
    setTransLoading(true);
    try {
      await apiClient.patch(`/missoes/${transModal.missao.id}/transicao`, {
        status_novo: transModal.target,
        motivo: transMotivo || undefined,
      });
      message.success(`Missão: ${transModal.label.toLowerCase()} com sucesso.`);
      setTransModal(null);
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro na transição de status.');
    } finally {
      setTransLoading(false);
    }
  };

  // History
  const openHistory = async (missao: MissaoResponse) => {
    setHistoryMissao(missao);
    setHistoryLoading(true);
    try {
      const { data } = await apiClient.get<HistoricoStatusMissaoResponse[]>(
        `/missoes/${missao.id}/historico`,
      );
      setHistory(data);
    } catch {
      message.error('Erro ao carregar histórico.');
    } finally {
      setHistoryLoading(false);
    }
  };

  // Baterias
  const openBaterias = async (missao: MissaoResponse) => {
    setBatMissao(missao);
    setBatLoading(true);
    try {
      const { data } = await apiClient.get<MissaoBateriaResponse[]>(
        `/missoes/${missao.id}/baterias`,
      );
      setBatList(data);
    } catch {
      message.error('Erro ao carregar baterias.');
    } finally {
      setBatLoading(false);
    }
  };

  const handleAddBateria = async (values: Record<string, unknown>) => {
    if (!batMissao) return;
    setBatAdding(true);
    try {
      await apiClient.post(`/missoes/${batMissao.id}/baterias`, {
        bateria_id: values.bateria_id,
        ordem_uso: values.ordem_uso,
      });
      message.success('Bateria associada.');
      setBatFormOpen(false);
      openBaterias(batMissao);
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao associar bateria.');
    } finally {
      setBatAdding(false);
    }
  };

  // Reservas insumo
  const openReservas = async (missao: MissaoResponse) => {
    setResMissao(missao);
    setResLoading(true);
    try {
      const { data } = await apiClient.get<ReservaInsumoResponse[]>(
        `/missoes/${missao.id}/reservas-insumo`,
      );
      setResList(data);
    } catch {
      message.error('Erro ao carregar reservas de insumo.');
    } finally {
      setResLoading(false);
    }
  };

  const handleAddReserva = async (values: Record<string, unknown>) => {
    if (!resMissao) return;
    setResAdding(true);
    try {
      await apiClient.post(`/missoes/${resMissao.id}/reservas-insumo`, {
        insumo_id: values.insumo_id,
        quantidade_prevista: values.quantidade_prevista,
        unidade_medida: values.unidade_medida,
      });
      message.success('Reserva de insumo criada.');
      setResFormOpen(false);
      openReservas(resMissao);
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao criar reserva.');
    } finally {
      setResAdding(false);
    }
  };

  // Execution
  const openExecucao = async (missao: MissaoResponse) => {
    setExecMissao(missao);
    execForm.setFieldsValue({
      area_realizada: missao.area_realizada,
      volume_realizado: missao.volume_realizado,
      observacoes_execucao: missao.observacoes_execucao,
    });
    // Load consumos
    setConsumosLoading(true);
    try {
      const { data } = await apiClient.get<ConsumoInsumoMissaoResponse[]>(
        `/missoes/${missao.id}/consumos-insumo`,
      );
      setConsumosList(data);
    } catch {
      message.error('Erro ao carregar consumos de insumo.');
    } finally {
      setConsumosLoading(false);
    }
    // Load evidencias
    setEvidenciasLoading(true);
    try {
      const { data } = await apiClient.get<{ items: EvidenciaResponse[] }>(
        '/evidencias', { params: { missao_id: missao.id, page_size: 100 } },
      );
      setEvidenciasList(data.items);
    } catch {
      message.error('Erro ao carregar evidências.');
    } finally {
      setEvidenciasLoading(false);
    }
  };

  const handleSaveExecucao = async () => {
    if (!execMissao) return;
    setExecSaving(true);
    try {
      const values = await execForm.validateFields();
      await apiClient.patch(`/missoes/${execMissao.id}/execucao`, {
        area_realizada: values.area_realizada,
        volume_realizado: values.volume_realizado,
        observacoes_execucao: values.observacoes_execucao,
      });
      message.success('Dados de execução salvos.');
      refresh();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      if (detail) {
        message.error(detail);
      }
    } finally {
      setExecSaving(false);
    }
  };

  const handleAddConsumo = async (values: Record<string, unknown>) => {
    if (!execMissao) return;
    setConsumoAdding(true);
    try {
      await apiClient.post(`/missoes/${execMissao.id}/consumos-insumo`, {
        insumo_id: values.insumo_id,
        quantidade_realizada: values.quantidade_realizada,
        unidade_medida: values.unidade_medida,
        observacoes: values.observacoes || null,
        justificativa_excesso: values.justificativa_excesso || null,
      });
      message.success('Consumo de insumo registrado.');
      setConsumoFormOpen(false);
      // Reload consumos
      const { data } = await apiClient.get<ConsumoInsumoMissaoResponse[]>(
        `/missoes/${execMissao.id}/consumos-insumo`,
      );
      setConsumosList(data);
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao registrar consumo.');
    } finally {
      setConsumoAdding(false);
    }
  };

  const handleUploadEvidencia = async (file: File) => {
    if (!execMissao) return;
    setEvidUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('missao_id', String(execMissao.id));
      if (evidLat != null) formData.append('latitude', String(evidLat));
      if (evidLng != null) formData.append('longitude', String(evidLng));
      await apiClient.post('/evidencias', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      message.success('Evidência enviada.');
      // Reload evidencias
      const { data } = await apiClient.get<{ items: EvidenciaResponse[] }>(
        '/evidencias', { params: { missao_id: execMissao.id, page_size: 100 } },
      );
      setEvidenciasList(data.items);
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao enviar evidência.');
    } finally {
      setEvidUploading(false);
    }
  };

  const transitionMenu = (record: MissaoResponse): MenuProps['items'] => {
    const items = TRANSITIONS[record.status] ?? [];
    if (!items.length) return [{ key: 'none', label: 'Sem transições', disabled: true }];
    return items.map((t) => ({
      key: t.target,
      label: t.label,
      danger: t.target === 'CANCELADA',
      onClick: () => openTransition(record, t.target, t.label),
    }));
  };

  const columns: ColumnsType<MissaoResponse> = [
    { title: 'Código', dataIndex: 'codigo', key: 'codigo', width: 120 },
    {
      title: 'OS', dataIndex: 'ordem_servico_id', key: 'ordem_servico_id', width: 120,
      render: (id: number) => lookupLabel(ordensServico.length ? ordensServico : [], id),
    },
    {
      title: 'Piloto', dataIndex: 'piloto_id', key: 'piloto_id',
      render: (id: number) => lookupLabel(pilotos, id),
    },
    {
      title: 'Drone', dataIndex: 'drone_id', key: 'drone_id',
      render: (id: number) => lookupLabel(drones, id),
    },
    { title: 'Data Agendada', dataIndex: 'data_agendada', key: 'data_agendada', width: 120 },
    {
      title: 'Status', dataIndex: 'status', key: 'status', width: 180,
      render: (s: MissaoStatus) => <StatusBadge status={s} />,
    },
    {
      title: 'Ações', key: 'acoes', width: 480,
      render: (_, record) => (
        <Space size="small" wrap>
          <Dropdown menu={{ items: transitionMenu(record) }}>
            <Button size="small">Ações <DownOutlined /></Button>
          </Dropdown>
          {record.status === 'EM_EXECUCAO' && (
            <Button size="small" type="primary" icon={<RocketOutlined />} onClick={() => openExecucao(record)}>
              Execução
            </Button>
          )}
          <Button size="small" icon={<HistoryOutlined />} onClick={() => openHistory(record)}>
            Histórico
          </Button>
          <Button size="small" icon={<ThunderboltOutlined />} onClick={() => openBaterias(record)}>
            Baterias
          </Button>
          <Button size="small" icon={<BulbOutlined />} onClick={() => openReservas(record)}>
            Insumos
          </Button>
        </Space>
      ),
    },
  ];

  const extraParams: Record<string, unknown> = {};
  if (filterStatus) extraParams.status = filterStatus;
  if (filterPiloto) extraParams.piloto_id = filterPiloto;
  if (filterDrone) extraParams.drone_id = filterDrone;
  if (filterData) extraParams.data_agendada = filterData;
  if (filterOS) extraParams.ordem_servico_id = filterOS;

  const needsMotivo = transModal?.target === 'CANCELADA';

  const historyColumns: ColumnsType<HistoricoStatusMissaoResponse> = [
    {
      title: 'De', dataIndex: 'status_anterior', key: 'status_anterior', width: 180,
      render: (s: string | null) => s ? <StatusBadge status={s} /> : <Tag>—</Tag>,
    },
    {
      title: 'Para', dataIndex: 'status_novo', key: 'status_novo', width: 180,
      render: (s: string) => <StatusBadge status={s} />,
    },
    { title: 'Motivo', dataIndex: 'motivo', key: 'motivo', render: (v: string | null) => v || '—' },
    {
      title: 'Data', dataIndex: 'created_at', key: 'created_at', width: 170,
      render: (d: string) => dayjs(d).format('DD/MM/YYYY HH:mm'),
    },
  ];

  const batColumns: ColumnsType<MissaoBateriaResponse> = [
    {
      title: 'Bateria', dataIndex: 'bateria_id', key: 'bateria_id',
      render: (id: number) => lookupLabel(baterias, id),
    },
    { title: 'Ordem de Uso', dataIndex: 'ordem_uso', key: 'ordem_uso', width: 120 },
    {
      title: 'Adicionada em', dataIndex: 'created_at', key: 'created_at', width: 170,
      render: (d: string) => dayjs(d).format('DD/MM/YYYY HH:mm'),
    },
  ];

  const resColumns: ColumnsType<ReservaInsumoResponse> = [
    {
      title: 'Insumo', dataIndex: 'insumo_id', key: 'insumo_id',
      render: (id: number) => lookupLabel(insumos, id),
    },
    { title: 'Qtd Prevista', dataIndex: 'quantidade_prevista', key: 'quantidade_prevista', width: 120 },
    { title: 'Unidade', dataIndex: 'unidade_medida', key: 'unidade_medida', width: 100 },
    {
      title: 'Criada em', dataIndex: 'created_at', key: 'created_at', width: 170,
      render: (d: string) => dayjs(d).format('DD/MM/YYYY HH:mm'),
    },
  ];

  return (
    <div>
      <Title level={2}>Missões</Title>
      <Text type="secondary">Gestão de missões de voo.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Select
          placeholder="Status"
          allowClear
          style={{ width: 200 }}
          options={STATUS_OPTIONS}
          onChange={(v) => setFilterStatus(v)}
        />
        <Select
          placeholder="Piloto"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 180 }}
          options={pilotos}
          onChange={(v) => setFilterPiloto(v)}
        />
        <Select
          placeholder="Drone"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 180 }}
          options={drones}
          onChange={(v) => setFilterDrone(v)}
        />
        <DatePicker
          placeholder="Data Agendada"
          onChange={(d) => setFilterData(d ? d.format('YYYY-MM-DD') : undefined)}
          format="DD/MM/YYYY"
        />
        <Select
          placeholder="Ordem de Serviço"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 180 }}
          options={ordensServico}
          onChange={(v) => setFilterOS(v)}
        />
      </Space>

      <DataTable<MissaoResponse>
        columns={columns}
        apiUrl="/missoes"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Nova Missão
          </Button>
        }
      />

      {/* Create Modal */}
      <FormModal
        open={modalOpen}
        title="Nova Missão"
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        width={700}
      >
        <Form.Item
          name="ordem_servico_id"
          label="Ordem de Serviço (Aprovada)"
          rules={[{ required: true, message: 'Selecione a OS' }]}
        >
          <Select options={ordensServico} showSearch optionFilterProp="label" placeholder="Selecione" />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="piloto_id"
              label="Piloto"
              rules={[{ required: true, message: 'Selecione o piloto' }]}
            >
              <Select options={pilotos} showSearch optionFilterProp="label" placeholder="Selecione" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="tecnico_id" label="Técnico">
              <Select options={tecnicos} showSearch optionFilterProp="label" placeholder="Selecione" allowClear />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item
          name="drone_id"
          label="Drone"
          rules={[{ required: true, message: 'Selecione o drone' }]}
        >
          <Select options={drones} showSearch optionFilterProp="label" placeholder="Selecione" />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="area_prevista"
              label="Área Prevista (ha)"
              rules={[{ required: true, message: 'Informe a área' }]}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="volume_previsto"
              label="Volume Previsto (L)"
              rules={[{ required: true, message: 'Informe o volume' }]}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="data_agendada"
              label="Data Agendada"
              rules={[{ required: true, message: 'Informe a data' }]}
            >
              <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="hora_agendada"
              label="Hora Agendada"
              rules={[{ required: true, message: 'Informe a hora' }]}
            >
              <TimePicker style={{ width: '100%' }} format="HH:mm" />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item name="observacoes_planejamento" label="Observações">
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
        okButtonProps={needsMotivo ? { danger: true } : undefined}
      >
        <p>
          Deseja {transModal?.label.toLowerCase()} a missão{' '}
          <strong>{transModal?.missao.codigo}</strong>?
        </p>
        {needsMotivo && (
          <Form.Item label="Motivo do Cancelamento" required>
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
        open={!!historyMissao}
        title={`Histórico — ${historyMissao?.codigo ?? ''}`}
        onCancel={() => setHistoryMissao(null)}
        footer={null}
        width={750}
      >
        <Table<HistoricoStatusMissaoResponse>
          columns={historyColumns}
          dataSource={history}
          rowKey="id"
          loading={historyLoading}
          pagination={false}
          size="small"
        />
      </Modal>

      {/* Baterias Modal */}
      <Modal
        open={!!batMissao}
        title={`Baterias — ${batMissao?.codigo ?? ''}`}
        onCancel={() => { setBatMissao(null); setBatFormOpen(false); }}
        footer={null}
        width={650}
      >
        <Space style={{ marginBottom: 12 }}>
          <Button type="primary" size="small" icon={<PlusOutlined />} onClick={() => setBatFormOpen(true)}>
            Associar Bateria
          </Button>
        </Space>
        <Table<MissaoBateriaResponse>
          columns={batColumns}
          dataSource={batList}
          rowKey="id"
          loading={batLoading}
          pagination={false}
          size="small"
        />
        <FormModal
          open={batFormOpen}
          title="Associar Bateria"
          onCancel={() => setBatFormOpen(false)}
          onSubmit={handleAddBateria}
          loading={batAdding}
          width={400}
        >
          <Form.Item
            name="bateria_id"
            label="Bateria"
            rules={[{ required: true, message: 'Selecione a bateria' }]}
          >
            <Select options={baterias} showSearch optionFilterProp="label" placeholder="Selecione" />
          </Form.Item>
          <Form.Item
            name="ordem_uso"
            label="Ordem de Uso"
            rules={[{ required: true, message: 'Informe a ordem' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
        </FormModal>
      </Modal>

      {/* Reservas Insumo Modal */}
      <Modal
        open={!!resMissao}
        title={`Reservas de Insumo — ${resMissao?.codigo ?? ''}`}
        onCancel={() => { setResMissao(null); setResFormOpen(false); }}
        footer={null}
        width={700}
      >
        <Space style={{ marginBottom: 12 }}>
          <Button type="primary" size="small" icon={<PlusOutlined />} onClick={() => setResFormOpen(true)}>
            Nova Reserva
          </Button>
        </Space>
        <Table<ReservaInsumoResponse>
          columns={resColumns}
          dataSource={resList}
          rowKey="id"
          loading={resLoading}
          pagination={false}
          size="small"
        />
        <FormModal
          open={resFormOpen}
          title="Nova Reserva de Insumo"
          onCancel={() => setResFormOpen(false)}
          onSubmit={handleAddReserva}
          loading={resAdding}
          width={450}
        >
          <Form.Item
            name="insumo_id"
            label="Insumo"
            rules={[{ required: true, message: 'Selecione o insumo' }]}
          >
            <Select options={insumos} showSearch optionFilterProp="label" placeholder="Selecione" />
          </Form.Item>
          <Form.Item
            name="quantidade_prevista"
            label="Quantidade Prevista"
            rules={[{ required: true, message: 'Informe a quantidade' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="unidade_medida"
            label="Unidade de Medida"
            rules={[{ required: true, message: 'Informe a unidade' }]}
          >
            <Input maxLength={30} placeholder="Ex: L, kg, mL" />
          </Form.Item>
        </FormModal>
      </Modal>

      {/* Execution Modal */}
      <Modal
        open={!!execMissao}
        title={`Execução — ${execMissao?.codigo ?? ''}`}
        onCancel={() => { setExecMissao(null); setConsumoFormOpen(false); execForm.resetFields(); setEvidLat(null); setEvidLng(null); }}
        footer={null}
        width={900}
      >
        <Tabs
          items={[
            {
              key: 'dados',
              label: 'Dados de Execução',
              children: (
                <Form form={execForm} layout="vertical">
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item name="area_realizada" label="Área Realizada (ha)">
                        <InputNumber min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item name="volume_realizado" label="Volume Realizado (L)">
                        <InputNumber min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>
                  <Form.Item name="observacoes_execucao" label="Observações da Execução">
                    <Input.TextArea rows={3} maxLength={2000} />
                  </Form.Item>
                  <Button type="primary" loading={execSaving} onClick={handleSaveExecucao}>
                    Salvar Dados de Execução
                  </Button>
                </Form>
              ),
            },
            {
              key: 'consumos',
              label: 'Consumo de Insumos',
              children: (
                <>
                  <Space style={{ marginBottom: 12 }}>
                    <Button type="primary" size="small" icon={<PlusOutlined />} onClick={() => setConsumoFormOpen(true)}>
                      Registrar Consumo
                    </Button>
                  </Space>
                  <Table<ConsumoInsumoMissaoResponse>
                    columns={[
                      { title: 'Insumo', dataIndex: 'insumo_id', key: 'insumo_id', render: (id: number) => lookupLabel(insumos, id) },
                      { title: 'Qtd Realizada', dataIndex: 'quantidade_realizada', key: 'quantidade_realizada', width: 120 },
                      { title: 'Unidade', dataIndex: 'unidade_medida', key: 'unidade_medida', width: 100 },
                      { title: 'Observações', dataIndex: 'observacoes', key: 'observacoes', render: (v: string | null) => v || '—' },
                      { title: 'Just. Excesso', dataIndex: 'justificativa_excesso', key: 'justificativa_excesso', render: (v: string | null) => v || '—' },
                      { title: 'Data', dataIndex: 'created_at', key: 'created_at', width: 150, render: (d: string) => dayjs(d).format('DD/MM/YYYY HH:mm') },
                    ]}
                    dataSource={consumosList}
                    rowKey="id"
                    loading={consumosLoading}
                    pagination={false}
                    size="small"
                  />
                  <FormModal
                    open={consumoFormOpen}
                    title="Registrar Consumo de Insumo"
                    onCancel={() => setConsumoFormOpen(false)}
                    onSubmit={handleAddConsumo}
                    loading={consumoAdding}
                    width={500}
                  >
                    <Form.Item name="insumo_id" label="Insumo" rules={[{ required: true, message: 'Selecione o insumo' }]}>
                      <Select options={insumos} showSearch optionFilterProp="label" placeholder="Selecione" />
                    </Form.Item>
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item name="quantidade_realizada" label="Quantidade Realizada" rules={[{ required: true, message: 'Informe a quantidade' }]}>
                          <InputNumber min={0} style={{ width: '100%' }} />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item name="unidade_medida" label="Unidade de Medida" rules={[{ required: true, message: 'Informe a unidade' }]}>
                          <Input maxLength={30} placeholder="Ex: L, kg, mL" />
                        </Form.Item>
                      </Col>
                    </Row>
                    <Form.Item name="observacoes" label="Observações">
                      <Input.TextArea rows={2} maxLength={2000} />
                    </Form.Item>
                    <Form.Item name="justificativa_excesso" label="Justificativa de Excesso" extra="Obrigatório quando a quantidade excede a reserva">
                      <Input.TextArea rows={2} maxLength={2000} />
                    </Form.Item>
                  </FormModal>
                </>
              ),
            },
            {
              key: 'evidencias',
              label: 'Evidências',
              children: (
                <>
                  <Divider>Upload de Evidência</Divider>
                  <Row gutter={16} style={{ marginBottom: 16 }}>
                    <Col span={8}>
                      <Typography.Text type="secondary" style={{ fontSize: 12 }}>Latitude</Typography.Text>
                      <InputNumber
                        value={evidLat}
                        onChange={(v) => setEvidLat(v)}
                        min={-90} max={90} step={0.000001} precision={6}
                        placeholder="-23.550520"
                        style={{ width: '100%' }}
                      />
                    </Col>
                    <Col span={8}>
                      <Typography.Text type="secondary" style={{ fontSize: 12 }}>Longitude</Typography.Text>
                      <InputNumber
                        value={evidLng}
                        onChange={(v) => setEvidLng(v)}
                        min={-180} max={180} step={0.000001} precision={6}
                        placeholder="-46.633308"
                        style={{ width: '100%' }}
                      />
                    </Col>
                    <Col span={8} style={{ display: 'flex', alignItems: 'flex-end' }}>
                      <Upload
                        accept=".jpg,.jpeg,.png,.mp4,.pdf"
                        maxCount={1}
                        showUploadList={false}
                        customRequest={async (options) => {
                          try {
                            await handleUploadEvidencia(options.file as File);
                            options.onSuccess?.(null);
                          } catch {
                            options.onError?.(new Error('Falha no upload'));
                          }
                        }}
                      >
                        <Button icon={<UploadOutlined />} loading={evidUploading}>Enviar Evidência</Button>
                      </Upload>
                    </Col>
                  </Row>
                  <Divider>Evidências Enviadas</Divider>
                  <Table<EvidenciaResponse>
                    columns={[
                      { title: 'Arquivo', dataIndex: 'nome_arquivo', key: 'nome_arquivo' },
                      { title: 'Tipo', dataIndex: 'tipo_arquivo', key: 'tipo_arquivo', width: 100, render: (v: string | null) => v || '—' },
                      { title: 'Latitude', dataIndex: 'latitude', key: 'latitude', width: 110, render: (v: number | null) => v != null ? v.toFixed(6) : '—' },
                      { title: 'Longitude', dataIndex: 'longitude', key: 'longitude', width: 110, render: (v: number | null) => v != null ? v.toFixed(6) : '—' },
                      { title: 'Data', dataIndex: 'created_at', key: 'created_at', width: 150, render: (d: string) => dayjs(d).format('DD/MM/YYYY HH:mm') },
                    ]}
                    dataSource={evidenciasList}
                    rowKey="id"
                    loading={evidenciasLoading}
                    pagination={false}
                    size="small"
                  />
                </>
              ),
            },
          ]}
        />
      </Modal>
    </div>
  );
}
