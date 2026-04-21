import { useState } from 'react';
import {
  Button, Card, Col, DatePicker, Empty, message,
  Row, Space, Spin, Statistic, Table, Tabs, Typography,
} from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { Dayjs } from 'dayjs';
import apiClient from '../api/client';
import StatusBadge from '../components/StatusBadge';
import type {
  MissoesPorStatusResponse,
  MissoesPorStatusItem,
  AreaPorClienteResponse,
  AreaPorClienteItem,
  FinanceiroResumoResponse,
  UtilizacaoDroneResponse,
  UtilizacaoDroneItem,
} from '../types/relatorio';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

export default function Relatorios() {
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('missoes');

  // Report data
  const [missoesPorStatus, setMissoesPorStatus] = useState<MissoesPorStatusResponse | null>(null);
  const [areaPorCliente, setAreaPorCliente] = useState<AreaPorClienteResponse | null>(null);
  const [finResumo, setFinResumo] = useState<FinanceiroResumoResponse | null>(null);
  const [utilDrones, setUtilDrones] = useState<UtilizacaoDroneResponse | null>(null);

  const getParams = () => {
    if (!dateRange) return null;
    return {
      data_inicio: dateRange[0].format('YYYY-MM-DD'),
      data_fim: dateRange[1].format('YYYY-MM-DD'),
    };
  };

  const fetchReport = async () => {
    const params = getParams();
    if (!params) {
      message.warning('Selecione o período.');
      return;
    }
    setLoading(true);
    try {
      const [missoes, area, fin, drones] = await Promise.all([
        apiClient.get<MissoesPorStatusResponse>('/relatorios/missoes-por-status', { params }),
        apiClient.get<AreaPorClienteResponse>('/relatorios/area-por-cliente', { params }),
        apiClient.get<FinanceiroResumoResponse>('/relatorios/financeiro', { params }),
        apiClient.get<UtilizacaoDroneResponse>('/relatorios/utilizacao-drones', { params }),
      ]);
      setMissoesPorStatus(missoes.data);
      setAreaPorCliente(area.data);
      setFinResumo(fin.data);
      setUtilDrones(drones.data);
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao carregar relatórios.');
    } finally {
      setLoading(false);
    }
  };

  // Columns for Missões por Status
  const missaoColumns: ColumnsType<MissoesPorStatusItem> = [
    {
      title: 'Status', dataIndex: 'status', key: 'status',
      render: (s: string) => <StatusBadge status={s} />,
    },
    {
      title: 'Total', dataIndex: 'total', key: 'total', width: 120,
      render: (v: number) => <strong>{v}</strong>,
    },
  ];

  // Columns for Área por Cliente
  const areaColumns: ColumnsType<AreaPorClienteItem> = [
    { title: 'Cliente', dataIndex: 'cliente_nome', key: 'cliente_nome' },
    {
      title: 'Área Pulverizada (ha)', dataIndex: 'area_total_pulverizada', key: 'area',
      render: (v: number) => v.toLocaleString('pt-BR', { minimumFractionDigits: 2 }),
    },
  ];

  // Columns for Utilização de Drones
  const droneColumns: ColumnsType<UtilizacaoDroneItem> = [
    { title: 'Identificação', dataIndex: 'drone_identificacao', key: 'ident' },
    { title: 'Modelo', dataIndex: 'drone_modelo', key: 'modelo' },
    {
      title: 'Horas Voadas', dataIndex: 'horas_voadas_periodo', key: 'horas',
      render: (v: number) => v.toLocaleString('pt-BR', { minimumFractionDigits: 1 }),
    },
    { title: 'Missões', dataIndex: 'total_missoes', key: 'missoes', width: 100 },
  ];

  const periodoLabel = dateRange
    ? `${dateRange[0].format('DD/MM/YYYY')} — ${dateRange[1].format('DD/MM/YYYY')}`
    : '';

  return (
    <div>
      <Title level={2}>Relatórios</Title>
      <Text type="secondary">Relatórios operacionais e financeiros.</Text>

      <Space style={{ margin: '16px 0' }}>
        <RangePicker
          format="DD/MM/YYYY"
          onChange={(dates) => {
            if (dates && dates[0] && dates[1]) {
              setDateRange([dates[0], dates[1]]);
            } else {
              setDateRange(null);
            }
          }}
        />
        <Button
          type="primary"
          icon={<SearchOutlined />}
          onClick={fetchReport}
          loading={loading}
        >
          Gerar Relatórios
        </Button>
      </Space>

      {loading && (
        <div style={{ textAlign: 'center', padding: 48 }}>
          <Spin size="large" />
        </div>
      )}

      {!loading && missoesPorStatus && (
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'missoes',
              label: 'Missões por Status',
              children: (
                <Card title={`Missões por Status — ${periodoLabel}`} size="small">
                  <Statistic
                    title="Total Geral"
                    value={missoesPorStatus.total_geral}
                    style={{ marginBottom: 16 }}
                  />
                  <Table<MissoesPorStatusItem>
                    columns={missaoColumns}
                    dataSource={missoesPorStatus.items}
                    rowKey="status"
                    pagination={false}
                    size="small"
                  />
                </Card>
              ),
            },
            {
              key: 'area',
              label: 'Área Pulverizada',
              children: (
                <Card title={`Área Pulverizada por Cliente — ${periodoLabel}`} size="small">
                  {areaPorCliente && areaPorCliente.items.length > 0 ? (
                    <Table<AreaPorClienteItem>
                      columns={areaColumns}
                      dataSource={areaPorCliente.items}
                      rowKey="cliente_id"
                      pagination={false}
                      size="small"
                    />
                  ) : (
                    <Empty description="Sem dados para o período selecionado" />
                  )}
                </Card>
              ),
            },
            {
              key: 'financeiro',
              label: 'Financeiro',
              children: (
                <Card title={`Resumo Financeiro — ${periodoLabel}`} size="small">
                  {finResumo && (
                    <Row gutter={[16, 16]}>
                      <Col span={6}>
                        <Statistic
                          title="Custo Estimado"
                          value={finResumo.total_custo_estimado}
                          precision={2}
                          prefix="R$"
                        />
                      </Col>
                      <Col span={6}>
                        <Statistic
                          title="Custo Realizado"
                          value={finResumo.total_custo_realizado}
                          precision={2}
                          prefix="R$"
                        />
                      </Col>
                      <Col span={6}>
                        <Statistic
                          title="Valor Faturado"
                          value={finResumo.total_valor_faturado}
                          precision={2}
                          prefix="R$"
                        />
                      </Col>
                      <Col span={6}>
                        <Statistic
                          title="Total Missões"
                          value={finResumo.total_missoes}
                        />
                      </Col>
                    </Row>
                  )}
                </Card>
              ),
            },
            {
              key: 'drones',
              label: 'Utilização de Drones',
              children: (
                <Card title={`Utilização de Drones — ${periodoLabel}`} size="small">
                  {utilDrones && utilDrones.items.length > 0 ? (
                    <Table<UtilizacaoDroneItem>
                      columns={droneColumns}
                      dataSource={utilDrones.items}
                      rowKey="drone_id"
                      pagination={false}
                      size="small"
                    />
                  ) : (
                    <Empty description="Sem dados para o período selecionado" />
                  )}
                </Card>
              ),
            },
          ]}
        />
      )}

      {!loading && !missoesPorStatus && (
        <Empty
          description="Selecione um período e clique em Gerar Relatórios"
          style={{ marginTop: 48 }}
        />
      )}
    </div>
  );
}
