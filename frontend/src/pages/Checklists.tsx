import { useCallback, useEffect, useState } from 'react';
import {
  Alert, Button, Card, Col, Empty, Form, Input, message, Modal,
  Row, Select, Space, Table, Tag, Typography,
} from 'antd';
import {
  CheckCircleOutlined, CloseCircleOutlined, ExclamationCircleOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import StatusBadge from '../components/StatusBadge';
import apiClient from '../api/client';
import type {
  ChecklistMissaoResponse,
  ItemChecklistMissaoResponse,
} from '../types/checklist';
import type { ItemChecklistStatus, MissaoStatus } from '../types/enums';
import type { MissaoResponse } from '../types/missao';

const { Title, Text } = Typography;

type DropdownOption = { value: number; label: string; status: MissaoStatus };

const ITEM_STATUS_OPTIONS: { value: ItemChecklistStatus; label: string }[] = [
  { value: 'APROVADO', label: 'Aprovado' },
  { value: 'REPROVADO', label: 'Reprovado' },
  { value: 'NAO_APLICAVEL', label: 'Não Aplicável' },
];

export default function Checklists() {
  const [missoes, setMissoes] = useState<DropdownOption[]>([]);
  const [selectedMissaoId, setSelectedMissaoId] = useState<number | undefined>();
  const [checklist, setChecklist] = useState<ChecklistMissaoResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Item edit modal
  const [editItem, setEditItem] = useState<ItemChecklistMissaoResponse | null>(null);
  const [itemStatus, setItemStatus] = useState<ItemChecklistStatus>('PENDENTE');
  const [itemObs, setItemObs] = useState('');
  const [itemSaving, setItemSaving] = useState(false);

  // Load missions that are in EM_CHECKLIST or nearby states
  useEffect(() => {
    apiClient
      .get<{ items: MissaoResponse[] }>('/missoes', { params: { page_size: 500 } })
      .then(({ data }) => {
        const relevant = data.items.filter((m) =>
          ['EM_CHECKLIST', 'LIBERADA'].includes(m.status),
        );
        setMissoes(
          relevant.map((m) => ({
            value: m.id,
            label: `${m.codigo} — ${m.status.replace(/_/g, ' ')}`,
            status: m.status,
          })),
        );
      });
  }, []);

  const loadChecklist = useCallback(async (missaoId: number) => {
    setLoading(true);
    try {
      const { data } = await apiClient.get<ChecklistMissaoResponse>(
        `/missoes/${missaoId}/checklist`,
      );
      setChecklist(data);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      if ((err as { response?: { status?: number } })?.response?.status === 404) {
        setChecklist(null);
        message.info(detail || 'Nenhum checklist encontrado para esta missão.');
      } else {
        message.error(detail || 'Erro ao carregar checklist.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSelectMissao = (id: number) => {
    setSelectedMissaoId(id);
    loadChecklist(id);
  };

  // Open item edit
  const openEditItem = (item: ItemChecklistMissaoResponse) => {
    setEditItem(item);
    setItemStatus(item.status_item === 'PENDENTE' ? 'APROVADO' : item.status_item);
    setItemObs(item.observacao ?? '');
  };

  const handleUpdateItem = async () => {
    if (!editItem || !selectedMissaoId) return;
    // Validate: mandatory + REPROVADO requires observation
    if (editItem.obrigatorio && itemStatus === 'REPROVADO' && !itemObs.trim()) {
      message.warning('Item obrigatório reprovado exige observação.');
      return;
    }
    setItemSaving(true);
    try {
      await apiClient.patch(
        `/missoes/${selectedMissaoId}/checklist/itens/${editItem.id}`,
        {
          status_item: itemStatus,
          observacao: itemObs || null,
        },
      );
      message.success('Item atualizado.');
      setEditItem(null);
      loadChecklist(selectedMissaoId);
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao atualizar item.');
    } finally {
      setItemSaving(false);
    }
  };

  // Concluir checklist (Piloto)
  const handleConcluir = async () => {
    if (!selectedMissaoId) return;
    setActionLoading(true);
    try {
      await apiClient.post(`/missoes/${selectedMissaoId}/checklist/concluir`);
      message.success('Checklist concluído.');
      loadChecklist(selectedMissaoId);
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao concluir checklist.');
    } finally {
      setActionLoading(false);
    }
  };

  // Aprovar checklist (Técnico)
  const handleAprovar = async () => {
    if (!selectedMissaoId) return;
    setActionLoading(true);
    try {
      await apiClient.post(`/missoes/${selectedMissaoId}/checklist/aprovar`);
      message.success('Checklist aprovado. Missão liberada.');
      loadChecklist(selectedMissaoId);
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao aprovar checklist.');
    } finally {
      setActionLoading(false);
    }
  };

  const itemStatusIcon = (status: ItemChecklistStatus) => {
    switch (status) {
      case 'APROVADO':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'REPROVADO':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'NAO_APLICAVEL':
        return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
      default:
        return null;
    }
  };

  const columns: ColumnsType<ItemChecklistMissaoResponse> = [
    {
      title: 'Item',
      dataIndex: 'nome_item',
      key: 'nome_item',
      render: (name: string, record) => (
        <Space>
          <span>{name}</span>
          {record.obrigatorio && (
            <Tag color="red" style={{ fontSize: 11 }}>Obrigatório</Tag>
          )}
        </Space>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status_item',
      key: 'status_item',
      width: 160,
      render: (s: ItemChecklistStatus) => (
        <Space>
          {itemStatusIcon(s)}
          <StatusBadge status={s} />
        </Space>
      ),
    },
    {
      title: 'Observação',
      dataIndex: 'observacao',
      key: 'observacao',
      ellipsis: true,
      render: (v: string | null) => v || '—',
    },
    {
      title: 'Ação',
      key: 'acao',
      width: 120,
      render: (_, record) => {
        const canEdit =
          checklist?.status_geral === 'PENDENTE' ||
          checklist?.status_geral === 'EM_PREENCHIMENTO';
        return canEdit ? (
          <Button size="small" onClick={() => openEditItem(record)}>
            Preencher
          </Button>
        ) : null;
      },
    },
  ];

  const canConcluir =
    checklist &&
    (checklist.status_geral === 'PENDENTE' || checklist.status_geral === 'EM_PREENCHIMENTO');

  const canAprovar = checklist && checklist.status_geral === 'CONCLUIDO';

  const hasReprovadoObrigatorio = checklist?.itens?.some(
    (i) => i.obrigatorio && i.status_item === 'REPROVADO',
  );

  return (
    <div>
      <Title level={2}>Checklists de Missão</Title>
      <Text type="secondary">
        Preenchimento e aprovação de checklists pré-voo.
      </Text>

      <Row style={{ margin: '16px 0' }}>
        <Col span={12}>
          <Select
            placeholder="Selecione uma missão"
            showSearch
            optionFilterProp="label"
            style={{ width: '100%' }}
            options={missoes}
            onChange={handleSelectMissao}
            value={selectedMissaoId}
          />
        </Col>
      </Row>

      {!selectedMissaoId && (
        <Empty description="Selecione uma missão para visualizar o checklist." />
      )}

      {selectedMissaoId && checklist && (
        <Card
          title={
            <Space>
              <SafetyCertificateOutlined />
              <span>Checklist — Missão {selectedMissaoId}</span>
              <StatusBadge status={checklist.status_geral} />
            </Space>
          }
          loading={loading}
          extra={
            <Space>
              <Text type="secondary">
                Preenchido em: {dayjs(checklist.preenchido_em).format('DD/MM/YYYY HH:mm')}
              </Text>
              {checklist.revisado_em && (
                <Text type="secondary">
                  | Revisado em: {dayjs(checklist.revisado_em).format('DD/MM/YYYY HH:mm')}
                </Text>
              )}
            </Space>
          }
        >
          {hasReprovadoObrigatorio && (
            <Alert
              type="warning"
              showIcon
              message="Existem itens obrigatórios reprovados. O checklist não pode ser aprovado até que sejam corrigidos."
              style={{ marginBottom: 16 }}
            />
          )}

          <Table<ItemChecklistMissaoResponse>
            columns={columns}
            dataSource={checklist.itens}
            rowKey="id"
            pagination={false}
            size="small"
            rowClassName={(record) =>
              record.obrigatorio && record.status_item === 'REPROVADO'
                ? 'ant-table-row-warning'
                : ''
            }
          />

          <Space style={{ marginTop: 16 }}>
            {canConcluir && (
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                loading={actionLoading}
                onClick={handleConcluir}
              >
                Concluir Checklist
              </Button>
            )}
            {canAprovar && (
              <Button
                type="primary"
                style={{ background: '#52c41a', borderColor: '#52c41a' }}
                icon={<SafetyCertificateOutlined />}
                loading={actionLoading}
                onClick={handleAprovar}
              >
                Aprovar Checklist (Técnico)
              </Button>
            )}
          </Space>
        </Card>
      )}

      {selectedMissaoId && !checklist && !loading && (
        <Empty description="Nenhum checklist encontrado para esta missão." />
      )}

      {/* Item Edit Modal */}
      <Modal
        open={!!editItem}
        title={`Preencher Item: ${editItem?.nome_item ?? ''}`}
        onCancel={() => setEditItem(null)}
        onOk={handleUpdateItem}
        confirmLoading={itemSaving}
        okText="Salvar"
        cancelText="Cancelar"
      >
        {editItem?.obrigatorio && (
          <Alert
            type="info"
            showIcon
            message="Este item é obrigatório. Se reprovado, a observação é obrigatória."
            style={{ marginBottom: 16 }}
          />
        )}
        <Form layout="vertical">
          <Form.Item label="Status" required>
            <Select
              options={ITEM_STATUS_OPTIONS}
              value={itemStatus}
              onChange={(v) => setItemStatus(v)}
            />
          </Form.Item>
          <Form.Item
            label="Observação"
            required={editItem?.obrigatorio && itemStatus === 'REPROVADO'}
          >
            <Input.TextArea
              rows={3}
              value={itemObs}
              onChange={(e) => setItemObs(e.target.value)}
              placeholder={
                editItem?.obrigatorio && itemStatus === 'REPROVADO'
                  ? 'Obrigatório para item reprovado'
                  : 'Opcional'
              }
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
