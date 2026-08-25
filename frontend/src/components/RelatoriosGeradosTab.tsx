import { useCallback, useEffect, useState } from 'react';
import { Button, Col, DatePicker, Form, Row, Select, Space, Table, Tag, message } from 'antd';
import { DeleteOutlined, DownloadOutlined, MailOutlined, SearchOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import apiClient from '../api/client';
import { downloadRelatorio, listarRelatorios } from '../api/relatoriosMedicao';
import type { RelatorioMedicaoListItem } from '../types/relatorio-medicao';
import ConfirmarExclusaoRelatorioModal from './ConfirmarExclusaoRelatorioModal';
import EnviarRelatorioModal from './EnviarRelatorioModal';

const { RangePicker } = DatePicker;

interface ClienteOption {
  id: number;
  nome: string;
}

export default function RelatoriosGeradosTab() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<RelatorioMedicaoListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // Clientes options
  const [clientes, setClientes] = useState<ClienteOption[]>([]);
  const [loadingClientes, setLoadingClientes] = useState(false);

  // Modals
  const [excluirModalOpen, setExcluirModalOpen] = useState(false);
  const [enviarModalOpen, setEnviarModalOpen] = useState(false);
  const [selectedRelatorio, setSelectedRelatorio] = useState<RelatorioMedicaoListItem | null>(null);

  // Load clientes
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

  const fetchData = useCallback(async (p: number, ps: number) => {
    setLoading(true);
    try {
      const values = form.getFieldsValue();
      const params: Record<string, unknown> = {
        page: p,
        page_size: ps,
      };
      if (values.cliente_id) params.cliente_id = values.cliente_id;
      if (values.status) params.status = values.status;
      if (values.periodo && values.periodo[0] && values.periodo[1]) {
        params.data_inicial = values.periodo[0].format('YYYY-MM-DD');
        params.data_final = values.periodo[1].format('YYYY-MM-DD');
      }

      const result = await listarRelatorios(params as Parameters<typeof listarRelatorios>[0]);
      setData(result.items);
      setTotal(result.total);
    } catch {
      message.error('Erro ao carregar relatórios');
    } finally {
      setLoading(false);
    }
  }, [form]);

  // Load on mount
  useEffect(() => {
    fetchData(1, pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSearch = () => {
    setPage(1);
    fetchData(1, pageSize);
  };

  const handlePageChange = (newPage: number, newPageSize: number) => {
    setPage(newPage);
    setPageSize(newPageSize);
    fetchData(newPage, newPageSize);
  };

  const handleDownload = async (relatorio: RelatorioMedicaoListItem) => {
    try {
      const result = await downloadRelatorio(relatorio.id);
      window.open(result.download_url, '_blank');
    } catch {
      message.error('Erro ao gerar link de download');
    }
  };

  const handleExcluirClick = (relatorio: RelatorioMedicaoListItem) => {
    setSelectedRelatorio(relatorio);
    setExcluirModalOpen(true);
  };

  const handleEnviarClick = (relatorio: RelatorioMedicaoListItem) => {
    setSelectedRelatorio(relatorio);
    setEnviarModalOpen(true);
  };

  const handleModalSuccess = () => {
    setExcluirModalOpen(false);
    setEnviarModalOpen(false);
    setSelectedRelatorio(null);
    fetchData(page, pageSize);
  };

  const columns: ColumnsType<RelatorioMedicaoListItem> = [
    {
      title: 'Cliente',
      dataIndex: 'cliente_nome',
      key: 'cliente_nome',
    },
    {
      title: 'Período',
      key: 'periodo',
      width: 200,
      render: (_, record) =>
        `${dayjs(record.data_inicial).format('DD/MM/YYYY')} - ${dayjs(record.data_final).format('DD/MM/YYYY')}`,
    },
    {
      title: 'Área Total (ha)',
      dataIndex: 'total_area',
      key: 'total_area',
      width: 130,
      align: 'right',
      render: (val: number) => Number(val).toFixed(2),
    },
    {
      title: 'Qtd Missões',
      dataIndex: 'qtd_missoes',
      key: 'qtd_missoes',
      width: 110,
      align: 'center',
    },
    {
      title: 'Data Geração',
      dataIndex: 'gerado_em',
      key: 'gerado_em',
      width: 160,
      render: (val: string) => dayjs(val).format('DD/MM/YYYY HH:mm'),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (val: string) => (
        <Tag color={val === 'ATIVO' ? 'green' : 'red'}>{val}</Tag>
      ),
    },
    {
      title: 'Ações',
      key: 'acoes',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(record)}
            disabled={record.status !== 'ATIVO'}
            title="Download"
          />
          <Button
            type="link"
            size="small"
            icon={<MailOutlined />}
            onClick={() => handleEnviarClick(record)}
            disabled={record.status !== 'ATIVO'}
            title="Enviar por e-mail"
          />
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleExcluirClick(record)}
            disabled={record.status !== 'ATIVO'}
            title="Excluir"
          />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Form form={form} layout="inline" style={{ marginBottom: 16 }}>
        <Row gutter={[8, 8]} style={{ width: '100%' }}>
          <Col xs={24} sm={8} md={6}>
            <Form.Item name="cliente_id" style={{ width: '100%' }}>
              <Select
                placeholder="Cliente"
                allowClear
                loading={loadingClientes}
                showSearch
                optionFilterProp="label"
                options={clientes.map((c) => ({ value: c.id, label: c.nome }))}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={8} md={6}>
            <Form.Item name="periodo" style={{ width: '100%' }}>
              <RangePicker format="DD/MM/YYYY" style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={4} md={4}>
            <Form.Item name="status" style={{ width: '100%' }}>
              <Select
                placeholder="Status"
                allowClear
                options={[
                  { value: 'ATIVO', label: 'Ativo' },
                  { value: 'EXCLUIDO', label: 'Excluído' },
                ]}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={4} md={3}>
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              Filtrar
            </Button>
          </Col>
        </Row>
      </Form>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={{
          current: page,
          pageSize,
          total,
          showSizeChanger: true,
          showTotal: (t) => `Total: ${t} relatórios`,
          onChange: handlePageChange,
        }}
        scroll={{ x: 900 }}
        locale={{ emptyText: 'Nenhum relatório encontrado' }}
      />

      <ConfirmarExclusaoRelatorioModal
        open={excluirModalOpen}
        relatorio={selectedRelatorio}
        onClose={() => { setExcluirModalOpen(false); setSelectedRelatorio(null); }}
        onSuccess={handleModalSuccess}
      />

      <EnviarRelatorioModal
        open={enviarModalOpen}
        relatorio={selectedRelatorio}
        onClose={() => { setEnviarModalOpen(false); setSelectedRelatorio(null); }}
        onSuccess={handleModalSuccess}
      />
    </div>
  );
}
