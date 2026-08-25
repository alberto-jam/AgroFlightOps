import { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Button, Card, message, Space, Spin, Table, Typography,
} from 'antd';
import { FileTextOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import apiClient from '../api/client';

const { Title, Text } = Typography;

interface PreviewState {
  missao_ids: number[];
  cliente_id: number;
  data_inicial: string;
  data_final: string;
}

interface MissaoPreviewItem {
  id: number;
  codigo: string;
  propriedade_nome: string;
  talhao_nome: string;
  area_realizada: number | null;
  encerrado_tecnicamente_em: string;
}

interface PreviewResponse {
  cliente_nome: string;
  missoes: MissaoPreviewItem[];
  total_area: number;
}

export default function MedicaoRopPreview() {
  const location = useLocation();
  const navigate = useNavigate();

  const state = location.state as PreviewState | undefined;

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [previewData, setPreviewData] = useState<PreviewResponse | null>(null);

  // Redirect if no valid state
  useEffect(() => {
    if (!state || !state.missao_ids?.length || !state.cliente_id || !state.data_inicial || !state.data_final) {
      navigate('/medicao-rop', { replace: true });
    }
  }, [state, navigate]);

  const fetchPreview = useCallback(async () => {
    if (!state) return;
    setLoading(true);
    try {
      const { data } = await apiClient.post<PreviewResponse>('/medicoes-rop/preview', {
        missao_ids: state.missao_ids,
        cliente_id: state.cliente_id,
      });
      setPreviewData(data);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao carregar preview do relatório');
      navigate('/medicao-rop', { replace: true });
    } finally {
      setLoading(false);
    }
  }, [state, navigate]);

  useEffect(() => {
    if (state?.missao_ids?.length) {
      fetchPreview();
    }
  }, [fetchPreview, state]);

  const handleCancel = () => {
    navigate('/medicao-rop');
  };

  const handleGenerate = async () => {
    if (!state) return;
    setGenerating(true);
    try {
      const { data } = await apiClient.post('/medicoes-rop/gerar-relatorio', {
        missao_ids: state.missao_ids,
        cliente_id: state.cliente_id,
        data_inicial: state.data_inicial,
        data_final: state.data_final,
      });
      message.success(data.mensagem || 'Relatório gerado com sucesso!');
      navigate('/medicao-rop', { replace: true });
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao gerar relatório de medição');
    } finally {
      setGenerating(false);
    }
  };

  const columns: ColumnsType<MissaoPreviewItem> = [
    {
      title: 'Código',
      dataIndex: 'codigo',
      key: 'codigo',
      width: 140,
    },
    {
      title: 'Propriedade',
      dataIndex: 'propriedade_nome',
      key: 'propriedade_nome',
    },
    {
      title: 'Talhão',
      dataIndex: 'talhao_nome',
      key: 'talhao_nome',
    },
    {
      title: 'Área Realizada (ha)',
      dataIndex: 'area_realizada',
      key: 'area_realizada',
      width: 150,
      align: 'right',
      render: (val: number | null) => val != null ? Number(val).toFixed(2) : '-',
    },
    {
      title: 'Encerramento Técnico',
      dataIndex: 'encerrado_tecnicamente_em',
      key: 'encerrado_tecnicamente_em',
      width: 180,
      render: (val: string) => val ? dayjs(val).format('DD/MM/YYYY HH:mm') : '-',
    },
  ];

  if (!state) {
    return null;
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
        <Spin size="large" tip="Carregando preview..." />
      </div>
    );
  }

  if (!previewData) {
    return null;
  }

  const periodoFormatado = `${dayjs(state.data_inicial).format('DD/MM/YYYY')} a ${dayjs(state.data_final).format('DD/MM/YYYY')}`;

  return (
    <div>
      <Title level={3}>
        <FileTextOutlined /> Relatório de Medição
      </Title>

      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" size={4}>
          <Text strong>Cliente:</Text>
          <Text>{previewData.cliente_nome}</Text>
          <Text strong style={{ marginTop: 8 }}>Período:</Text>
          <Text>{periodoFormatado}</Text>
        </Space>
      </Card>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={previewData.missoes}
        pagination={false}
        scroll={{ x: 800 }}
        footer={() => (
          <div style={{ textAlign: 'right' }}>
            <Text strong>
              Área Total: {Number(previewData.total_area).toFixed(2)} ha
            </Text>
          </div>
        )}
      />

      <div style={{ marginTop: 24, display: 'flex', justifyContent: 'flex-end' }}>
        <Space>
          <Button onClick={handleCancel}>
            Cancelar
          </Button>
          <Button
            type="primary"
            loading={generating}
            disabled={generating}
            onClick={handleGenerate}
          >
            Gerar Documento
          </Button>
        </Space>
      </div>
    </div>
  );
}
