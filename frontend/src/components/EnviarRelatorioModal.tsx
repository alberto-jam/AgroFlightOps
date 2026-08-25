import { Form, Input, Modal, message } from 'antd';
import { useState } from 'react';
import { enviarRelatorio } from '../api/relatoriosMedicao';
import type { RelatorioMedicaoListItem } from '../types/relatorio-medicao';

const { TextArea } = Input;

interface Props {
  open: boolean;
  relatorio: RelatorioMedicaoListItem | null;
  onClose: () => void;
  onSuccess: () => void;
}

function validateEmails(value: string): { valid: string[]; invalid: string[] } {
  const raw = value.split(/[,\n]+/).map((e) => e.trim()).filter(Boolean);
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const valid: string[] = [];
  const invalid: string[] = [];
  for (const email of raw) {
    if (emailRegex.test(email)) {
      valid.push(email);
    } else {
      invalid.push(email);
    }
  }
  return { valid, invalid };
}

export default function EnviarRelatorioModal({ open, relatorio, onClose, onSuccess }: Props) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!relatorio) return;

    try {
      const values = await form.validateFields();
      const emailsText: string = values.emails;
      const { valid, invalid } = validateEmails(emailsText);

      if (invalid.length > 0) {
        message.error(`E-mails inválidos: ${invalid.join(', ')}`);
        return;
      }

      if (valid.length === 0) {
        message.error('Informe pelo menos um e-mail válido');
        return;
      }

      setLoading(true);
      await enviarRelatorio(relatorio.id, {
        emails: valid,
        mensagem: values.mensagem || null,
      });
      message.success('Relatório enviado com sucesso');
      form.resetFields();
      onSuccess();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao enviar relatório');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title="Enviar Relatório por E-mail"
      open={open}
      onCancel={handleClose}
      onOk={handleSubmit}
      okText="Enviar"
      okButtonProps={{ loading }}
      cancelText="Cancelar"
      destroyOnClose
    >
      <Form form={form} layout="vertical">
        <Form.Item
          name="emails"
          label="E-mails (separados por vírgula ou nova linha)"
          rules={[{ required: true, message: 'Informe pelo menos um e-mail' }]}
        >
          <TextArea
            rows={3}
            placeholder="cliente@empresa.com, outro@empresa.com"
          />
        </Form.Item>
        <Form.Item
          name="mensagem"
          label="Mensagem personalizada (opcional)"
        >
          <TextArea
            rows={3}
            placeholder="Segue o relatório de medição conforme solicitado..."
          />
        </Form.Item>
      </Form>
    </Modal>
  );
}
