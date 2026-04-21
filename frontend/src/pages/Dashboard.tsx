import { useEffect, useState } from 'react';
import {
  Alert, Card, Col, List, Row, Space, Spin, Statistic, Table, Tag, Typography,
} from 'antd';
import {
  AimOutlined, CheckCircleOutlined, DashboardOutlined, FileTextOutlined,
  RocketOutlined, WarningOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import apiClient from '../api/client';
import StatusBadge from '../components/StatusBadge';
import type { OrdemServicoResponse } from '../types/ordem-servico';
import type { MissaoResponse } from '../types/missao';
import type { DroneResponse } from '../types/drone';
import type { DocumentoOficialResponse } from '../types/documento-oficial';

const { Title, Text } = Typography;

interface DashboardData {
  osTotal: number;
  osPorStatus: Record<string, number>;
  missoesAtivas: number;
  missoesPorStatus: Record<string, number>;
  dronesDisponiveis: number;
  dronesTotal: number;
  dronesEmUso: number;
  docsVencidos: DocumentoOficialResponse[];
  missoesRecentes: MissaoResponse[];
}

const CARD_STYLE = { borderRadius: 8 };

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const [osRes, missoesRes, dronesRes, docsRes] = await Promise.all([
        apiClient.get<{ items: OrdemServicoResponse[]; total: number }>(
          '/ordens-servico', { params: { page_size: 100 } },
        ),
        apiClient.get<{ items: MissaoResponse[]; total: number }>(
          '/missoes', { params: { page_size: 100 } },
        ),
        apiClient.get<{ items: DroneResponse[]; total: number }>(
          '/drones', { params: { page_size: 100 } },
        ),
        apiClient.get<{ items: DocumentoOficialResponse[]; total: number }>(
          '/documentos-oficiais', { params: { page_size: 100, status: 'VENCIDO' } },
        ).catch(() => ({ data: { items: [], total: 0 } })),
      ]);

      const osList = osRes.data.items;
      const missoesList = missoesRes.data.items;
      const dronesList = dronesRes.data.items;

      // OS por status
      const osPorStatus: Record<string, number> = {};
      osList.forEach((os) => {
        osPorStatus[os.status] = (osPorStatus[os.status] || 0) + 1;
      });

      // Missões por status
      const missoesPorStatus: Record<string, number> = {};
      const statusAtivos = ['EM_EXECUCAO', 'PAUSADA', 'AGENDADA', 'LIBERADA', 'EM_CHECKLIST'];
      let missoesAtivas = 0;
      missoesList.forEach((m) => {
        missoesPorStatus[m.status] = (missoesPorStatus[m.status] || 0) + 1;
        if (statusAtivos.includes(m.status)) missoesAtivas++;
      });

      // Drones
      const dronesDisponiveis = dronesList.filter((d) => d.status === 'DISPONIVEL').length;
      const dronesEmUso = dronesList.filter((d) => d.status === 'EM_USO').length;

      // Missões recentes (últimas 5 por data)
      const missoesRecentes = [...missoesList]
        .sort((a, b) => dayjs(b.updated_at).valueOf() - dayjs(a.updated_at).valueOf())
        .slice(0, 5);

      setData({
        osTotal: osRes.data.total,
        osPorStatus,
        missoesAtivas,
        missoesPorStatus,
        dronesDisponiveis,
        dronesTotal: dronesList.length,
        dronesEmUso,
        docsVencidos: docsRes.data.items,
        missoesRecentes,
      });
    } catch {
      // Silently handle — partial data is fine
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text type="secondary">Carregando dashboard...</Text>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div>
        <Title level={2}>Dashboard</Title>
        <Alert type="warning" message="Não foi possível carregar os dados do dashboard." />
      </div>
    );
  }

  const recentColumns: ColumnsType<MissaoResponse> = [
    { title: 'Código', dataIndex: 'codigo', key: 'codigo', width: 120 },
    {
      title: 'Status', dataIndex: 'status', key: 'status', width: 200,
      render: (s: string) => <StatusBadge status={s} />,
    },
    {
      title: 'Data Agendada', dataIndex: 'data_agendada', key: 'data_agendada', width: 120,
      render: (d: string) => d ? dayjs(d).format('DD/MM/YYYY') : '—',
    },
    {
      title: 'Atualizado', dataIndex: 'updated_at', key: 'updated_at', width: 160,
      render: (d: string) => dayjs(d).format('DD/MM/YYYY HH:mm'),
    },
  ];

  return (
    <div>
      <Title level={2}>
        <DashboardOutlined style={{ marginRight: 8 }} />
        Dashboard
      </Title>

      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card style={CARD_STYLE}>
            <Statistic
              title="Ordens de Serviço"
              value={data.osTotal}
              prefix={<FileTextOutlined />}
            />
            <Space style={{ marginTop: 8 }} wrap>
              {Object.entries(data.osPorStatus).map(([status, count]) => (
                <span key={status}>
                  <StatusBadge status={status} /> {count}
                </span>
              ))}
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card style={CARD_STYLE}>
            <Statistic
              title="Missões Ativas"
              value={data.missoesAtivas}
              prefix={<AimOutlined />}
              valueStyle={{ color: data.missoesAtivas > 0 ? '#1890ff' : undefined }}
            />
            <Space style={{ marginTop: 8 }} wrap>
              {Object.entries(data.missoesPorStatus)
                .filter(([s]) => ['EM_EXECUCAO', 'PAUSADA', 'AGENDADA'].includes(s))
                .map(([status, count]) => (
                  <span key={status}>
                    <StatusBadge status={status} /> {count}
                  </span>
                ))}
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card style={CARD_STYLE}>
            <Statistic
              title="Drones Disponíveis"
              value={data.dronesDisponiveis}
              suffix={`/ ${data.dronesTotal}`}
              prefix={<RocketOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            {data.dronesEmUso > 0 && (
              <div style={{ marginTop: 8 }}>
                <Tag color="blue">Em uso: {data.dronesEmUso}</Tag>
              </div>
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card style={CARD_STYLE}>
            <Statistic
              title="Docs Vencidos"
              value={data.docsVencidos.length}
              prefix={<WarningOutlined />}
              valueStyle={{ color: data.docsVencidos.length > 0 ? '#ff4d4f' : '#52c41a' }}
            />
            {data.docsVencidos.length === 0 && (
              <div style={{ marginTop: 8 }}>
                <Tag color="green" icon={<CheckCircleOutlined />}>Tudo em dia</Tag>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Alerts for expired documents */}
      {data.docsVencidos.length > 0 && (
        <Alert
          type="warning"
          showIcon
          icon={<WarningOutlined />}
          message={`${data.docsVencidos.length} documento(s) vencido(s)`}
          description={
            <List
              size="small"
              dataSource={data.docsVencidos.slice(0, 5)}
              renderItem={(doc) => (
                <List.Item>
                  <Text>
                    {doc.tipo_documento} — {doc.entidade} #{doc.entidade_id}
                    {doc.data_validade && (
                      <Text type="danger"> (vencido em {dayjs(doc.data_validade).format('DD/MM/YYYY')})</Text>
                    )}
                  </Text>
                </List.Item>
              )}
            />
          }
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Recent Missions */}
      <Card title="Missões Recentes" size="small" style={CARD_STYLE}>
        <Table<MissaoResponse>
          columns={recentColumns}
          dataSource={data.missoesRecentes}
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  );
}
