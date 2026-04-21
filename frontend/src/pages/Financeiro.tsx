import { useCallback, useState } from 'react';
import {
  Button, Col, Descriptions, Form, Input, InputNumber, message, Modal,
  Row, Select, Space, Typography,
} from 'antd';
import { DollarOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import DataTable from '../components/DataTable';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type { MissaoResponse } from '../types/missao';
import type { MissaoStatus, FinanceiroStatus } from '../types/enums';
import type { FinanceiroMissaoResponse, FinanceiroMissaoUpdate } from '../types/financeiro';

const { Title, Text } = Typography;

const FINANCEIRO_STATUS_OPTIONS: { value: FinanceiroStatus; label: string }[] = [
  { value: 'PENDENTE', label: 'Pendente' },
  { value: 'EM_FATURAMENTO', label: 'Em Faturamento' },
  { value: 'FATURADO', label: 'Faturado' },
  { value: 'RECEBIDO', label: 'Recebido' },
  { value: 'CANCELADO', label: 'Cancelado' },
];

const MISSAO_STATUS_FILTER: { value: MissaoStatus; label: string }[] = [
  { value: 'ENCERRADA_TECNICAMENTE', label: 'Encerrada Tecnicamente' },
  { value: 'ENCERRADA_FINANCEIRAMENTE', label: 'Encerrada Financeiramente' },
];

export default function Financeiro() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [filterStatus, setFilterStatus] = useState<MissaoStatus | undefined>();

  // Detail / edit modal
  const [selectedMissao, setSelectedMissao] = useState<MissaoResponse | null>(null);
  const [financeiro, setFinanceiro] = useState<FinanceiroMissaoResponse | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm();

  // Encerrar modal
  const [encerrarMissao, setEncerrarMissao] = useState<MissaoResponse | null>(null);
  const [encerrarLoading, setEncerrarLoading] = useState(false);

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  const openDetail = async (missao: MissaoResponse) => {
    setSelectedMissao(missao);
    setLoadingDetail(true);
    try {
      const { data } = await apiClient.get<FinanceiroMissaoResponse>(
        `/missoes/${missao.id}/financeiro`,
      );
      setFinanceiro(data);
      form.setFieldsValue({
        custo_estimado: data.custo_estimado,
        custo_realizado: data.custo_realizado,
        valor_faturado: data.valor_faturado,
        status_financeiro: data.status_financeiro,
        observacoes: data.observacoes,
      });
    } catch (err: any) {
      if (err?.response?.status === 404) {
        message.info('Registro financeiro ainda não criado para esta missão.');
        setSelectedMissao(null);
      } else {
        message.error(err?.response?.data?.detail || 'Erro ao carregar dados financeiros.');
      }
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleSave = async () => {
    if (!selectedMissao || !financeiro) return;
    setSaving(true);
    try {
      const values = await form.validateFields();
      const payload: FinanceiroMissaoUpdate = {
        custo_estimado: values.custo_estimado,
        custo_realizado: values.custo_realizado,
        valor_faturado: values.valor_faturado,
        status_financeiro: values.status_financeiro,
        observacoes: values.observacoes || null,
      };
      const { data } = await apiClient.patch<FinanceiroMissaoResponse>(
        `/missoes/${selectedMissao.id}/financeiro`,
        payload,
      );
      setFinanceiro(data);
      message.success('Dados financeiros atualizados.');
      refresh();
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Erro ao salvar dados financeiros.');
    } finally {
      setSaving(false);
    }
  };

  const handleEncerrar = async () => {
    if (!encerrarMissao) return;
    setEncerrarLoading(true);
    try {
      await apiClient.post(`/missoes/${encerrarMissao.id}/financeiro/encerrar`);
      message.success('Missão encerrada financeiramente.');
      setEncerrarMissao(null);
      setSelectedMissao(null);
      refresh();
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Erro ao encerrar financeiramente.');
    } finally {
      setEncerrarLoading(false);
    }
  };

  const columns: ColumnsType<MissaoResponse> = [
    { title: 'Código', dataIndex: 'codigo', key: 'codigo', width: 130 },
    {
      title: 'Status Missão', dataIndex: 'status', key: 'status', width: 200,
      render: (s: MissaoStatus) => <StatusBadge status={s} />,
    },
    {
      title: 'Data Agendada', dataIndex: 'data_agendada', key: 'data_agendada', width: 130,
      render: (d: string) => d ? dayjs(d).format('DD/MM/YYYY') : '—',
    },
    {
      title: 'Enc. Técnico', dataIndex: 'encerrado_tecnicamente_em', key: 'enc_tec', width: 160,
      render: (d: string | null) => d ? dayjs(d).format('DD/MM/YYYY HH:mm') : '—',
    },
    {
      title: 'Enc. Financeiro', dataIndex: 'encerrado_financeiramente_em', key: 'enc_fin', width: 160,
      render: (d: string | null) => d ? dayjs(d).format('DD/MM/YYYY HH:mm') : '—',
    },
    {
      title: 'Ações', key: 'acoes', width: 200,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<DollarOutlined />}
            onClick={() => openDetail(record)}
          >
            Financeiro
          </Button>
        </Space>
      ),
    },
  ];

  const extraParams: Record<string, unknown> = {
    status: filterStatus || 'ENCERRADA_TECNICAMENTE',
  };

  return (
    <div>
      <Title level={2}>Financeiro</Title>
      <Text type="secondary">Gestão financeira de missões encerradas tecnicamente.</Text>

      <Space style={{ margin: '16px 0' }}>
        <Select
          placeholder="Status da Missão"
          allowClear
          style={{ width: 260 }}
          options={MISSAO_STATUS_FILTER}
          value={filterStatus}
          onChange={(v) => setFilterStatus(v)}
        />
      </Space>

      <DataTable<MissaoResponse>
        columns={columns}
        apiUrl="/missoes"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
      />

      {/* Detail / Edit Modal */}
      <Modal
        open={!!selectedMissao && !loadingDetail}
        title={`Financeiro — Missão ${selectedMissao?.codigo ?? ''}`}
        onCancel={() => { setSelectedMissao(null); setFinanceiro(null); form.resetFields(); }}
        footer={null}
        width={700}
      >
        {financeiro && (
          <>
            <Descriptions size="small" bordered column={2} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="Status Financeiro">
                <StatusBadge status={financeiro.status_financeiro} />
              </Descriptions.Item>
              <Descriptions.Item label="Criado em">
                {dayjs(financeiro.created_at).format('DD/MM/YYYY HH:mm')}
              </Descriptions.Item>
              {financeiro.fechado_em && (
                <Descriptions.Item label="Fechado em">
                  {dayjs(financeiro.fechado_em).format('DD/MM/YYYY HH:mm')}
                </Descriptions.Item>
              )}
            </Descriptions>

            <Form form={form} layout="vertical">
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    name="custo_estimado"
                    label="Custo Estimado (R$)"
                    rules={[{ type: 'number', min: 0, message: 'Valor deve ser >= 0' }]}
                  >
                    <InputNumber
                      min={0}
                      precision={2}
                      style={{ width: '100%' }}
                      prefix="R$"
                      disabled={selectedMissao?.status === 'ENCERRADA_FINANCEIRAMENTE'}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="custo_realizado"
                    label="Custo Realizado (R$)"
                    rules={[{ type: 'number', min: 0, message: 'Valor deve ser >= 0' }]}
                  >
                    <InputNumber
                      min={0}
                      precision={2}
                      style={{ width: '100%' }}
                      prefix="R$"
                      disabled={selectedMissao?.status === 'ENCERRADA_FINANCEIRAMENTE'}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="valor_faturado"
                    label="Valor Faturado (R$)"
                    rules={[{ type: 'number', min: 0, message: 'Valor deve ser >= 0' }]}
                  >
                    <InputNumber
                      min={0}
                      precision={2}
                      style={{ width: '100%' }}
                      prefix="R$"
                      disabled={selectedMissao?.status === 'ENCERRADA_FINANCEIRAMENTE'}
                    />
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="status_financeiro" label="Status Financeiro">
                    <Select
                      options={FINANCEIRO_STATUS_OPTIONS}
                      disabled={selectedMissao?.status === 'ENCERRADA_FINANCEIRAMENTE'}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="observacoes" label="Observações">
                    <Input.TextArea
                      rows={2}
                      maxLength={2000}
                      disabled={selectedMissao?.status === 'ENCERRADA_FINANCEIRAMENTE'}
                    />
                  </Form.Item>
                </Col>
              </Row>

              {selectedMissao?.status !== 'ENCERRADA_FINANCEIRAMENTE' && (
                <Space>
                  <Button type="primary" onClick={handleSave} loading={saving}>
                    Salvar
                  </Button>
                  <Button
                    danger
                    icon={<ExclamationCircleOutlined />}
                    onClick={() => setEncerrarMissao(selectedMissao)}
                  >
                    Encerrar Financeiramente
                  </Button>
                </Space>
              )}
            </Form>
          </>
        )}
      </Modal>

      {/* Encerrar Confirmation */}
      <Modal
        open={!!encerrarMissao}
        title="Confirmar Encerramento Financeiro"
        onCancel={() => setEncerrarMissao(null)}
        onOk={handleEncerrar}
        confirmLoading={encerrarLoading}
        okText="Encerrar"
        okButtonProps={{ danger: true }}
        cancelText="Cancelar"
      >
        <p>
          Deseja encerrar financeiramente a missão{' '}
          <strong>{encerrarMissao?.codigo}</strong>? Esta ação não pode ser desfeita.
        </p>
      </Modal>
    </div>
  );
}
