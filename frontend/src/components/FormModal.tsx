import { useEffect, type ReactNode } from 'react';
import { Modal, Form } from 'antd';
import type { FormInstance } from 'antd';

export interface FormModalProps<T = Record<string, unknown>> {
  /** Whether the modal is visible. */
  open: boolean;
  /** Modal title. */
  title: string;
  /** Called when the user cancels / closes the modal. */
  onCancel: () => void;
  /** Called with validated form values on submit. */
  onSubmit: (values: T) => void | Promise<void>;
  /** Pre-fill form for edit mode. `undefined` = create mode. */
  initialValues?: Partial<T>;
  /** Show a spinner on the OK button while saving. */
  loading?: boolean;
  /** Form fields rendered inside the modal body. */
  children: ReactNode | ((form: FormInstance<T>) => ReactNode);
  /** Modal width (default 600). */
  width?: number;
  /** Text for the OK button (default "Salvar"). */
  okText?: string;
}

export default function FormModal<T = Record<string, unknown>>({
  open,
  title,
  onCancel,
  onSubmit,
  initialValues,
  loading = false,
  children,
  width = 600,
  okText = 'Salvar',
}: FormModalProps<T>) {
  const [form] = Form.useForm<T>();

  // Reset & populate when modal opens or initialValues change
  useEffect(() => {
    if (open) {
      form.resetFields();
      if (initialValues) {
        form.setFieldsValue(initialValues as Parameters<typeof form.setFieldsValue>[0]);
      }
    }
  }, [open, initialValues, form]);

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      await onSubmit(values);
    } catch {
      // validation errors are shown inline by Ant Design
    }
  };

  return (
    <Modal
      open={open}
      title={title}
      onCancel={onCancel}
      onOk={handleOk}
      confirmLoading={loading}
      destroyOnHidden
      width={width}
      okText={okText}
      cancelText="Cancelar"
    >
      <Form form={form} layout="vertical" autoComplete="off">
        {typeof children === 'function' ? children(form) : children}
      </Form>
    </Modal>
  );
}
