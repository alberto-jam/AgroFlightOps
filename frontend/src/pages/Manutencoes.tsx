import { useCallback, useEffect, useState } from 'react';
import { Button, Col, DatePicker, Form, Input, InputNumber, Row, Select, Space, Typography, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import apiClient from '../api/client';
import type { ManutencaoResponse, ManutencaoCreate, ManutencaoUpdate } from '../types/manutencao';
import type { DroneResponse } from '../types/drone';

const { Title, Text } = Typography;

type DropdownOption = { value: number; label: string };

export default function Manutencoes() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<ManutencaoResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Filters
  const [filterDrone, setFilterDrone] = useState<number | undefined>();
  const [filterDataInicio, setFilterDataInicio] = useState<string | undefined>();
  const [filterDataFim, setFilterDataFim] = useState<string | undefined>();

  // Dropdown data
  const [drones, setDrones] = useState<DropdownOption[]>([]);

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  useEffect(() => {
    apiClient.get<{ items: DroneResponse[] }>('/drones', { params: { page_size: 200 } })
      .then(({ data }) =>
        setDrones(data.items.map((d) => ({ value: d.id, label: d.identificacao }))),
      );
  }, []);

  const lookupLabel = (list: DropdownOption[], id: number) =>
    list.find((o) => o.value === id)?.label ?? `#${id}`;

  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (record: ManutencaoResponse) => { setEditing(record); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); };

  const handleSubmit = async (values: Record<string, unknown>) => {
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {
        tipo: values.tipo,
        descricao: values.descricao || null,
        data_manutencao: dayjs(values.data_manutencao).format('YYYY-MM-DD'),
        proxima_manutencao: values.proxima_manutencao
          ? dayjs(values.proxima_manutencao).format('YYYY-MM-DD')
          : null,
        horas_na_data: values.horas_na_data ?? null,
      };

      if (editing) {
        await apiClient.put(`/manutencoes/${editing.id}`, payload as ManutencaoUpdate);
        message.success('Manutenção atualizada com sucesso.');
      } else {
        (payload as ManutencaoCreate & Record<string, unknown>).drone_id = values.drone_id;
        await apiClient.post('/manutencoes', payload);
        message.success('Manutenção criada com sucesso.');
      }
      closeModal();
      refresh();
    } catch (err: unknown) {
      message.error((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao salvar manutenção.');
    } finally {
      setSaving(false);
    }
  };

  const columns: ColumnsType<ManutencaoResponse> = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
    {
      title: 'Drone', dataIndex: 'drone_id', key: 'drone_id', width: 150,
      render: (id: number) => lookupLabel(drones, id),
    },
    { title: 'Tipo', dataIndex: 'tipo', key: 'tipo', width: 150 },
    { title: 'Descrição', dataIndex: 'descricao', key: 'descricao', ellipsis: true, render: (v: string | null) => v || '—' },
    {
      title: 'Data Manutenção', dataIndex: 'data_manutencao', key: 'data_manutencao', width: 150,
      render: (d: string) => dayjs(d).format('DD/MM/YYYY'),
    },
    {
      title: 'Próxima Manutenção', dataIndex: 'proxima_manutencao', key: 'proxima_manutencao', width: 170,
      render: (d: string | null) => d ? dayjs(d).format('DD/MM/YYYY') : '—',
    },
    {
      title: 'Horas na Data', dataIndex: 'horas_na_data', key: 'horas_na_data', width: 130,
      render: (v: number | null) => v != null ? v : '—',
    },
    {
      title: 'Ações', key: 'acoes', width: 100,
      render: (_, record) => (
        <Button size="small" onClick={() => openEdit(record)}>Editar</Button>
      ),
    },
  ];

  const extraParams: Record<string, unknown> = {};
  if (filterDrone) extraParams.drone_id = filterDrone;
  if (filterDataInicio) extraParams.data_inicio = filterDataInicio;
  if (filterDataFim) extraParams.data_fim = filterDataFim;

  return (
    <div>
      <Title level={2}>Manutenções</Title>
      <Text type="secondary">Registro de manutenções de drones.</Text>

      <Space style={{ margin: '16px 0', flexWrap: 'wrap' }}>
        <Select
          placeholder="Filtrar por Drone"
          allowClear
          showSearch
          optionFilterProp="label"
          style={{ width: 200 }}
          options={drones}
          onChange={(v) => setFilterDrone(v)}
        />
        <DatePicker
          placeholder="Data Início"
          onChange={(d) => setFilterDataInicio(d ? d.format('YYYY-MM-DD') : undefined)}
          format="DD/MM/YYYY"
        />
        <DatePicker
          placeholder="Data Fim"
          onChange={(d) => setFilterDataFim(d ? d.format('YYYY-MM-DD') : undefined)}
          format="DD/MM/YYYY"
        />
      </Space>

      <DataTable<ManutencaoResponse>
        columns={columns}
        apiUrl="/manutencoes"
        rowKey="id"
        extraParams={extraParams}
        refreshKey={refreshKey}
        toolbar={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            Nova Manutenção
          </Button>
        }
      />

      <FormModal<ManutencaoCreate & ManutencaoUpdate>
        open={modalOpen}
        title={editing ? 'Editar Manutenção' : 'Nova Manutenção'}
        onCancel={closeModal}
        onSubmit={handleSubmit}
        loading={saving}
        initialValues={
          editing
            ? {
                tipo: editing.tipo,
                descricao: editing.descricao,
                data_manutencao: dayjs(editing.data_manutencao),
                proxima_manutencao: editing.proxima_manutencao ? dayjs(editing.proxima_manutencao) : null,
                horas_na_data: editing.horas_na_data,
              } as any
            : undefined
        }
      >
        {!editing && (
          <Form.Item
            name="drone_id"
            label="Drone"
            rules={[{ required: true, message: 'Selecione o drone' }]}
          >
            <Select options={drones} showSearch optionFilterProp="label" placeholder="Selecione" />
          </Form.Item>
        )}
        <Form.Item
          name="tipo"
          label="Tipo"
          rules={[{ required: true, message: 'Informe o tipo de manutenção' }]}
        >
          <Input maxLength={120} />
        </Form.Item>
        <Form.Item name="descricao" label="Descrição">
          <Input.TextArea rows={3} maxLength={2000} />
        </Form.Item>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="data_manutencao"
              label="Data Manutenção"
              rules={[{ required: true, message: 'Informe a data' }]}
            >
              <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="proxima_manutencao" label="Próxima Manutenção">
              <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item name="horas_na_data" label="Horas na Data">
          <InputNumber min={0} step={0.1} style={{ width: '100%' }} />
        </Form.Item>
      </FormModal>
    </div>
  );
}
