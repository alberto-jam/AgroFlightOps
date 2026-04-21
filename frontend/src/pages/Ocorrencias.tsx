import { useEffect, useState } from 'react';
import { Button, Form, Input, Select, Space, Typography, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { OcorrenciaResponse, OcorrenciaCreate } from '../types/ocorrencia';
import type { Severidade } from '../types/enums';
import type { TipoOcorrenciaResponse } from '../types/tipo-ocorrencia';
import type { MissaoResponse } from '../types/missao';

const { Title, Text } = Typography;

const SEVERIDADE_OPTIONS: { value: Severidade; label: string }[] = [
  { value: 'BAIXA', label: 'Baixa' },
  { value: 'MEDIA', label: 'Média' },
  { value: 'ALTA', label: 'Alta' },
  { value: 'CRITICA', label: 'Crítica' },
];

type DropdownOption = { value: number; label: string };

export default function Ocorrencias() {
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Filters
  const [filterMissao, setFilterMissao] = useState<number | undefined>();
  const [filterTipo, setFilterTipo] = useState<number | undefined>();
  const [filterSeveridade, setFilterSeveridade] = useState<Severidade | undefined>();

  // Dropdown data
  const [missoes, setMissoes] = useState<DropdownOption[]>([]);
  const [tiposOcorrencia, setTiposOcorrencia] = useState<DropdownOption[]>([]);

  useEffect(() => {
    apiClient.get<{ items: MissaoResponse[] }>('/missoes', { params: { page_size: 200 } })
      .then(({ data }) =>
        setMissoes(data.items.map((m) => ({ value: m.id, label: m.codigo }))),
      );
    apiClient.get<{ items: TipoOcorrenciaResponse[] }>('/tipos-ocorrencia', { params: { page_size: 200 } })
      .then(({ data }) =>
        setTiposOcorrencia(data.items.map((t) => ({ value: t.id, label: t.nome }))),
      ).catch(() => {
        // endpoint may not exist yet
      });
  }, []);

  const lookupLabel = (list: DropdownOption[], id: number) =>
    list.find((o) => o.value === id)?.label ?? `#${id}`;

  const refresh = () => setRefreshKey((k) => k + 1);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
const handleSubmit = async (values: any) => {
    setSaving(true);
    try {
      const payload: OcorrenciaCreate = {
        missao_id: values.missao_id,
        tipo_ocorrencia_id: values.tipo_ocorrencia_id,
        descricao: values.descricao,
        severidade: values.severidade,
      };
      await apiClient.post('/ocorrencias', payload);
      message.success('Ocorrência registrada.');
      setModalOpen(false);
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao registrar ocorrência.');
    } finally {
      setSaving(false);
    }
  };

  const columns: ColumnsType<OcorrenciaResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    {
      title: 'Missão', dataIndex: 'missao_id', key: 'missao_id', width: 120,
      render: (id: number) => lookupLabel(missoes, id),
    },
    {
      title: 'Tipo', dataIndex: 'tipo_ocorrencia_id', key: 'tipo_ocorrencia_id',
      render: (id: number) => lookupLabel(tiposOcorrencia, id),
    },
    { title: 'Descrição', dataIndex: 'descricao', key: 'descricao', ellipsis: true },
    {
      title: 'Severidade', dataIndex: 'severidade', key: 'severidade', width: 120,
      render: (s: Severidade) => <StatusBadge status={s} />,
    },
    {
      title: 'Registrada em', dataIndex: 'registrada_em', key: 'registrada_em', width: 170,
      render: (d: string) => dayjs(d).format('DD/MM/YYYY HH:mm'),
    },
  ];

  const extraParams: Record<string, unknown> = {};
  if (filterMissao) extraParams.missao_id = filterMissao;
  if (filterTipo) extraParams.tipo_ocorrencia_id = filterTipo;
  if (filterSeveridade) extraParams.severidade = filterSeveridade;

  return (
    <div>
      <Title level={2}>Ocorrências</Title>
      <Text type="secondary">Registro de ocorrências durante missões.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Select
          placeholder="Missão"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 180 }}
          options={missoes}
          onChange={(v) => setFilterMissao(v)}
        />
        <Select
          placeholder="Tipo de Ocorrência"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 200 }}
          options={tiposOcorrencia}
          onChange={(v) => setFilterTipo(v)}
        />
        <Select
          placeholder="Severidade"
          allowClear
          style={{ width: 150 }}
          options={SEVERIDADE_OPTIONS}
          onChange={(v) => setFilterSeveridade(v)}
        />
      </Space>

      <DataTable<OcorrenciaResponse>
        columns={columns}
        apiUrl="/ocorrencias"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            Nova Ocorrência
          </Button>
        }
      />

      <FormModal
        open={modalOpen}
        title="Nova Ocorrência"
        onCancel={() => setModalOpen(false)}
        onSubmit={handleSubmit}
        loading={saving}
        width={600}
      >
        <Form.Item
          name="missao_id"
          label="Missão"
          rules={[{ required: true, message: 'Selecione a missão' }]}
        >
          <Select options={missoes} showSearch optionFilterProp="label" placeholder="Selecione" />
        </Form.Item>
        <Form.Item
          name="tipo_ocorrencia_id"
          label="Tipo de Ocorrência"
          rules={[{ required: true, message: 'Selecione o tipo' }]}
        >
          <Select options={tiposOcorrencia} showSearch optionFilterProp="label" placeholder="Selecione" />
        </Form.Item>
        <Form.Item
          name="descricao"
          label="Descrição"
          rules={[{ required: true, message: 'Informe a descrição' }]}
        >
          <Input.TextArea rows={3} maxLength={2000} />
        </Form.Item>
        <Form.Item
          name="severidade"
          label="Severidade"
          rules={[{ required: true, message: 'Selecione a severidade' }]}
        >
          <Select options={SEVERIDADE_OPTIONS} placeholder="Selecione" />
        </Form.Item>
      </FormModal>
    </div>
  );
}
