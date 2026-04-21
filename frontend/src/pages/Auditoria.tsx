import { useEffect, useState } from 'react';
import {
  DatePicker, Input, Modal, Select, Space, Tag, Typography,
} from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { type Dayjs } from 'dayjs';
import DataTable from '../components/DataTable';
import apiClient from '../api/client';
import type { AuditoriaResponse } from '../types/auditoria';
import type { UsuarioResponse } from '../types/usuario';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

const ENTIDADE_OPTIONS = [
  'usuario', 'cliente', 'cultura', 'propriedade', 'talhao',
  'drone', 'bateria', 'insumo', 'ordem_servico', 'missao', 'documento_oficial',
].map((e) => ({ value: e, label: e.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) }));

const ACAO_COLORS: Record<string, string> = {
  CREATE: 'green',
  UPDATE: 'blue',
  DELETE: 'red',
};

export default function Auditoria() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [filterEntidade, setFilterEntidade] = useState<string | undefined>();
  const [filterEntidadeId, setFilterEntidadeId] = useState<number | undefined>();
  const [filterUsuario, setFilterUsuario] = useState<number | undefined>();
  const [filterDates, setFilterDates] = useState<[Dayjs, Dayjs] | null>(null);

  const [usuarios, setUsuarios] = useState<{ value: number; label: string }[]>([]);

  // Detail modal
  const [detail, setDetail] = useState<AuditoriaResponse | null>(null);

  useEffect(() => {
    apiClient.get<{ items: UsuarioResponse[] }>('/usuarios', { params: { page_size: 100 } })
      .then(({ data }) =>
        setUsuarios(data.items.map((u) => ({ value: u.id, label: u.nome }))),
      )
      .catch(() => {});
  }, []);

  const lookupUsuario = (id: number) =>
    usuarios.find((u) => u.value === id)?.label ?? `#${id}`;

  const columns: ColumnsType<AuditoriaResponse> = [
    {
      title: 'Data', dataIndex: 'created_at', key: 'created_at', width: 170,
      render: (d: string) => dayjs(d).format('DD/MM/YYYY HH:mm:ss'),
    },
    {
      title: 'Entidade', dataIndex: 'entidade', key: 'entidade', width: 150,
      render: (e: string) => (
        <Tag>{e.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</Tag>
      ),
    },
    { title: 'ID Entidade', dataIndex: 'entidade_id', key: 'entidade_id', width: 100 },
    {
      title: 'Ação', dataIndex: 'acao', key: 'acao', width: 100,
      render: (a: string) => <Tag color={ACAO_COLORS[a] ?? 'default'}>{a}</Tag>,
    },
    {
      title: 'Usuário', dataIndex: 'usuario_id', key: 'usuario_id', width: 160,
      render: (id: number) => lookupUsuario(id),
    },
    {
      title: 'Detalhes', key: 'detalhes', width: 100,
      render: (_, record) => (
        <a onClick={() => setDetail(record)}>
          <EyeOutlined /> Ver
        </a>
      ),
    },
  ];

  const extraParams: Record<string, unknown> = {};
  if (filterEntidade) extraParams.entidade = filterEntidade;
  if (filterEntidadeId) extraParams.entidade_id = filterEntidadeId;
  if (filterUsuario) extraParams.usuario_id = filterUsuario;
  if (filterDates) {
    extraParams.data_inicio = filterDates[0].startOf('day').toISOString();
    extraParams.data_fim = filterDates[1].endOf('day').toISOString();
  }

  return (
    <div>
      <Title level={2}>Auditoria</Title>
      <Text type="secondary">Log de auditoria de operações do sistema.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Select
          placeholder="Entidade"
          allowClear
          style={{ width: 180 }}
          options={ENTIDADE_OPTIONS}
          onChange={(v) => { setFilterEntidade(v); setRefreshKey((k) => k + 1); }}
        />
        <Input
          placeholder="ID Entidade"
          allowClear
          style={{ width: 120 }}
          type="number"
          onChange={(e) => {
            const val = e.target.value ? Number(e.target.value) : undefined;
            setFilterEntidadeId(val);
            setRefreshKey((k) => k + 1);
          }}
        />
        <Select
          placeholder="Usuário"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 200 }}
          options={usuarios}
          onChange={(v) => { setFilterUsuario(v); setRefreshKey((k) => k + 1); }}
        />
        <RangePicker
          format="DD/MM/YYYY"
          onChange={(dates) => {
            if (dates && dates[0] && dates[1]) {
              setFilterDates([dates[0], dates[1]]);
            } else {
              setFilterDates(null);
            }
            setRefreshKey((k) => k + 1);
          }}
        />
      </Space>

      <DataTable<AuditoriaResponse>
        columns={columns}
        apiUrl="/auditoria"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
      />

      {/* Detail Modal */}
      <Modal
        open={!!detail}
        title={`Auditoria #${detail?.id ?? ''} — ${detail?.acao ?? ''} ${detail?.entidade ?? ''}`}
        onCancel={() => setDetail(null)}
        footer={null}
        width={800}
      >
        {detail && (
          <div>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div>
                <Text strong>Data: </Text>
                <Text>{dayjs(detail.created_at).format('DD/MM/YYYY HH:mm:ss')}</Text>
              </div>
              <div>
                <Text strong>Usuário: </Text>
                <Text>{lookupUsuario(detail.usuario_id)}</Text>
              </div>
              <div>
                <Text strong>Entidade: </Text>
                <Tag>{detail.entidade}</Tag>
                <Text strong> ID: </Text>
                <Text>{detail.entidade_id}</Text>
              </div>
              <div>
                <Text strong>Ação: </Text>
                <Tag color={ACAO_COLORS[detail.acao] ?? 'default'}>{detail.acao}</Tag>
              </div>

              {detail.valor_anterior && (
                <div>
                  <Text strong>Valor Anterior:</Text>
                  <pre style={{
                    background: '#f5f5f5',
                    padding: 12,
                    borderRadius: 6,
                    maxHeight: 300,
                    overflow: 'auto',
                    fontSize: 12,
                  }}>
                    {JSON.stringify(detail.valor_anterior, null, 2)}
                  </pre>
                </div>
              )}

              {detail.valor_novo && (
                <div>
                  <Text strong>Valor Novo:</Text>
                  <pre style={{
                    background: '#f0f9ff',
                    padding: 12,
                    borderRadius: 6,
                    maxHeight: 300,
                    overflow: 'auto',
                    fontSize: 12,
                  }}>
                    {JSON.stringify(detail.valor_novo, null, 2)}
                  </pre>
                </div>
              )}
            </Space>
          </div>
        )}
      </Modal>
    </div>
  );
}
