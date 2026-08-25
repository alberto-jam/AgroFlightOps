import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Button, Col, DatePicker, Form, message, Row, Select, Space, Table, Typography, Tag,
} from 'antd';
import { DollarOutlined, FilePdfOutlined, SearchOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import apiClient from '../api/client';

const { Title } = Typography;
const { RangePicker } = DatePicker;

interface ClienteOption {
  id: number;
  nome: string;
}

interface PropriedadeOption {
  id: number;
  nome: string;
}

interface MedicaoRopMissao {
  id: number;
  codigo: string;
  propriedade_nome: string;
  talhao_nome: string;
  encerrado_tecnicamente_em: string;
  area_realizada: number | null;
  status: string;
}

interface PaginatedResponse {
  items: MedicaoRopMissao[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export default function MedicaoRop() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<MedicaoRopMissao[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  // Options
  const [clientes, setClientes] = useState<ClienteOption[]>([]);
  const [propriedades, setPropriedades] = useState<PropriedadeOption[]>([]);
  const [loadingClientes, setLoadingClientes] = useState(false);
  const [loadingPropriedades, setLoadingPropriedades] = useState(false);

  // Track current filters for pagination
  const [currentFilters, setCurrentFilters] = useState<{
    cliente_id: number;
    data_inicial: string;
    data_final: string;
    propriedade_id?: number;
  } | null>(null);

  // Load clientes on mount
  useEffect(() => {
    const loadClientes = async () => {
      setLoadingClientes(true);
      try {
        const { data } = await apiClient.get('/clientes', { params: { page_size: 100 } });
        setClientes(data.items || data);
      } catch {
        message.error('Erro ao carregar clientes');
      } finally {
        setLoadingClientes(false);
      }
    };
    loadClientes();
  }, []);

  // Load propriedades when cliente changes
  const handleClienteChange = async (clienteId: number) => {
    form.setFieldValue('propriedade_id', undefined);
    setPropriedades([]);
    if (!clienteId) return;

    setLoadingPropriedades(true);
    try {
      const { data } = await apiClient.get('/propriedades', {
        params: { cliente_id: clienteId, page_size: 100 },
      });
      setPropriedades(data.items || data);
    } catch {
      message.error('Erro ao carregar propriedades');
    } finally {
      setLoadingPropriedades(false);
    }
  };

  const fetchData = useCallback(async (filters: {
    cliente_id: number;
    data_inicial: string;
    data_final: string;
    propriedade_id?: number;
  }, p: number, ps: number) => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        cliente_id: filters.cliente_id,
        data_inicial: filters.data_inicial,
        data_final: filters.data_final,
        page: p,
        page_size: ps,
      };
      if (filters.propriedade_id) {
        params.propriedade_id = filters.propriedade_id;
      }
      const { data } = await apiClient.get<PaginatedResponse>('/medicoes-rop', { params });
      setData(data.items);
      setTotal(data.total);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao consultar missões para medição');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSearch = async () => {
    try {
      const values = await form.validateFields();
      const [dataInicial, dataFinal] = values.periodo;
      const filters = {
        cliente_id: values.cliente_id,
        data_inicial: dataInicial.format('YYYY-MM-DD'),
        data_final: dataFinal.format('YYYY-MM-DD'),
        propriedade_id: values.propriedade_id || undefined,
      };
      setCurrentFilters(filters);
      setPage(1);
      setSelectedRowKeys([]);
      await fetchData(filters, 1, pageSize);
    } catch {
      // validation error — antd shows field errors
    }
  };

  const handlePageChange = (newPage: number, newPageSize: number) => {
    setPage(newPage);
    setPageSize(newPageSize);
    if (currentFilters) {
      fetchData(currentFilters, newPage, newPageSize);
    }
  };

  const columns: ColumnsType<MedicaoRopMissao> = [
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
      title: 'Encerramento Técnico',
      dataIndex: 'encerrado_tecnicamente_em',
      key: 'encerrado_tecnicamente_em',
      width: 180,
      render: (val: string) => val ? dayjs(val).format('DD/MM/YYYY HH:mm') : '-',
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
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 180,
      render: (val: string) => <Tag color="green">{val.replace(/_/g, ' ')}</Tag>,
    },
  ];

  return (
    <div>
      <Title level={3}>
        <DollarOutlined /> Medição ROP
      </Title>

      <Form form={form} layout="vertical" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          <Col xs={24} sm={12} md={6}>
            <Form.Item
              name="cliente_id"
              label="Cliente"
              rules={[{ required: true, message: 'Selecione o cliente' }]}
            >
              <Select
                placeholder="Selecione o cliente"
                loading={loadingClientes}
                showSearch
                optionFilterProp="label"
                onChange={handleClienteChange}
                options={clientes.map((c) => ({ value: c.id, label: c.nome }))}
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Form.Item name="propriedade_id" label="Propriedade">
              <Select
                placeholder="Todas"
                allowClear
                loading={loadingPropriedades}
                showSearch
                optionFilterProp="label"
                options={propriedades.map((p) => ({ value: p.id, label: p.nome }))}
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Form.Item
              name="periodo"
              label="Período"
              rules={[{ required: true, message: 'Selecione o período' }]}
            >
              <RangePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={4} style={{ display: 'flex', alignItems: 'flex-end' }}>
            <Form.Item style={{ marginBottom: 24 }}>
              <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                Consultar
              </Button>
            </Form.Item>
          </Col>
        </Row>
      </Form>

      {selectedRowKeys.length > 0 && (
        <Space style={{ marginBottom: 16 }}>
          <Typography.Text strong>
            {selectedRowKeys.length} missão(ões) selecionada(s)
          </Typography.Text>
        </Space>
      )}

      <Space style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<FilePdfOutlined />}
          disabled={selectedRowKeys.length === 0}
          onClick={() => {
            navigate('/medicao-rop/preview', {
              state: {
                missao_ids: selectedRowKeys.map((key) => Number(key)),
                cliente_id: currentFilters?.cliente_id,
                data_inicial: currentFilters?.data_inicial,
                data_final: currentFilters?.data_final,
              },
            });
          }}
        >
          Gerar Relatório
        </Button>
      </Space>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        rowSelection={{
          selectedRowKeys,
          onChange: setSelectedRowKeys,
        }}
        pagination={{
          current: page,
          pageSize,
          total,
          showSizeChanger: true,
          showTotal: (t) => `Total: ${t} missões`,
          onChange: handlePageChange,
        }}
        locale={{ emptyText: currentFilters ? 'Nenhuma missão elegível encontrada para os filtros aplicados' : 'Utilize os filtros acima para consultar' }}
        scroll={{ x: 900 }}
      />
    </div>
  );
}
