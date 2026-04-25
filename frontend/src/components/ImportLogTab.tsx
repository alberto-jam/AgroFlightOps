import { useRef, useState } from 'react';
import { Button, message, Space, Spin, Table, Typography } from 'antd';
import { DeleteOutlined, UploadOutlined, SaveOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import apiClient from '../api/client';

interface ImportLogTabProps {
  missaoId: number;
}

interface FileEntry {
  uid: string;
  name: string;
  file: File;
}

export default function ImportLogTab({ missaoId }: ImportLogTabProps) {
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleButtonClick = () => {
    setLoading(true);
    message.loading({ content: 'Aguarde, selecionando arquivo...', key: 'file-load', duration: 0 });
    // Small delay to ensure the loading state renders before the file picker opens
    setTimeout(() => inputRef.current?.click(), 50);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (!selectedFiles || selectedFiles.length === 0) {
      setLoading(false);
      message.destroy('file-load');
      return;
    }
    const newEntries: FileEntry[] = [];
    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      const exists = files.some((f) => f.name === file.name);
      if (!exists) {
        newEntries.push({ uid: `${Date.now()}-${file.name}`, name: file.name, file });
      }
    }
    if (newEntries.length > 0) {
      setFiles((prev) => [...prev, ...newEntries]);
      message.success({ content: `${newEntries.length} arquivo(s) carregado(s).`, key: 'file-load' });
    } else {
      message.warning({ content: 'Arquivo(s) já estão na lista.', key: 'file-load' });
    }
    setLoading(false);
    // Reset input so the same file can be selected again
    if (inputRef.current) inputRef.current.value = '';
  };

  const handleRemove = (uid: string) => {
    setFiles((prev) => prev.filter((f) => f.uid !== uid));
  };

  const handleSave = async () => {
    if (!files.length) {
      message.warning('Selecione pelo menos um arquivo.');
      return;
    }
    setUploading(true);
    let successCount = 0;
    let errorCount = 0;
    for (const entry of files) {
      try {
        const formData = new FormData();
        formData.append('file', entry.file);
        await apiClient.post(`/missoes/${missaoId}/telemetria`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        successCount++;
      } catch {
        errorCount++;
      }
    }
    setUploading(false);
    if (successCount > 0) {
      message.success(`${successCount} arquivo(s) enviado(s) com sucesso.`);
    }
    if (errorCount > 0) {
      message.error(`${errorCount} arquivo(s) com erro no envio.`);
    }
    setFiles([]);
  };

  const columns: ColumnsType<FileEntry> = [
    { title: 'Arquivo', dataIndex: 'name', key: 'name' },
    {
      title: 'Ação', key: 'action', width: 100,
      render: (_, record) => (
        <Button
          size="small"
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleRemove(record.uid)}
        >
          Excluir
        </Button>
      ),
    },
  ];

  return (
    <Spin spinning={loading} tip="Carregando arquivo...">
      <div>
        <Typography.Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          Selecione os arquivos de log da missão (JSON) para importar ao Data Lake de telemetria.
        </Typography.Text>

        <input
          ref={inputRef}
          type="file"
          accept=".json"
          multiple
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />

        <Space style={{ marginBottom: 16 }}>
          <Button icon={<UploadOutlined />} onClick={handleButtonClick} loading={loading}>
            {loading ? 'Carregando arquivo...' : 'Importar Arquivo de Log'}
          </Button>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={uploading}
            disabled={!files.length}
          >
            {uploading ? 'Enviando arquivos...' : 'Salvar'}
          </Button>
        </Space>

        <Table<FileEntry>
          columns={columns}
          dataSource={files}
          rowKey="uid"
          pagination={false}
          size="small"
          locale={{ emptyText: 'Nenhum arquivo selecionado' }}
        />
      </div>
    </Spin>
  );
}
