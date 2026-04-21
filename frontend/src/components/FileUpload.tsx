import { useState } from 'react';
import { Upload, Button, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';

export interface FileUploadProps {
  /** Accepted file types (e.g. ".pdf,.jpg,.png"). */
  accept?: string;
  /** Max number of files (default 1). */
  maxCount?: number;
  /** Allow multiple file selection. */
  multiple?: boolean;
  /** Called when a file is ready to upload. Return a promise that resolves on success. */
  onUpload: (file: File) => Promise<void>;
  /** Optional label for the upload button. */
  buttonText?: string;
}

export default function FileUpload({
  accept,
  maxCount = 1,
  multiple = false,
  onUpload,
  buttonText = 'Selecionar arquivo',
}: FileUploadProps) {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);

  const handleUpload: UploadProps['customRequest'] = async (options) => {
    const file = options.file as File;
    setUploading(true);
    try {
      await onUpload(file);
      options.onSuccess?.(null);
      message.success(`${file.name} enviado com sucesso`);
    } catch {
      options.onError?.(new Error('Falha no upload'));
      message.error(`Falha ao enviar ${file.name}`);
    } finally {
      setUploading(false);
    }
  };

  const handleChange: UploadProps['onChange'] = ({ fileList: newFileList }) => {
    setFileList(newFileList);
  };

  return (
    <Upload
      accept={accept}
      maxCount={maxCount}
      multiple={multiple}
      fileList={fileList}
      customRequest={handleUpload}
      onChange={handleChange}
    >
      <Button icon={<UploadOutlined />} loading={uploading}>
        {buttonText}
      </Button>
    </Upload>
  );
}
