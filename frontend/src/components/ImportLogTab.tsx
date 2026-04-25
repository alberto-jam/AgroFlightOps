import { useState } from 'react';
import { Button, message, Space, Table, Typography, Upload } from 'antd';
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

  const handleSelect = (file: File) => {
    message.loading({ content: 'Carregando arquivo...', key: 'file-loading', duration: 0 });
    setTimeout(() => {
      const exists = files.some((f) => f.name === file.name);
      if (exists) {
        message.warning({ content: `Arquivo "${file.name}" já está na lista.`, key: 'file-loading' });
      } else {
        setFiles((prev) => [
          ...prev,
          { uid: `${Date.now()}-${file.name}`, name: file.name, file },
        ]);
        message.success({ content: `Arquivo "${file.name}" carregado.`, key: 'file-loading' });
      }
    }, 50);
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
    <div>
      <Typography.Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
        Selecione os arquivos de log da missão (JSON) para importar ao Data Lake de telemetria.
      </Typography.Text>

      <Space style={{ marginBottom: 16 }}>
        <Upload
          accept=".json"
          multiple
          showUploadList={false}
          beforeUpload={(file) => {
            handleSelect(file);
            return false;
          }}
        >
          <Button icon={<UploadOutlined />}>Importar Arquivo de Log</Button>
        </Upload>
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
  );
}
