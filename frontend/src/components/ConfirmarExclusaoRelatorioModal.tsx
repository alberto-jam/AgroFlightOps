import { Modal, message } from 'antd';
import dayjs from 'dayjs';
import { useState } from 'react';
import { excluirRelatorio } from '../api/relatoriosMedicao';
import type { RelatorioMedicaoListItem } from '../types/relatorio-medicao';

interface Props {
  open: boolean;
  relatorio: RelatorioMedicaoListItem | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function ConfirmarExclusaoRelatorioModal({ open, relatorio, onClose, onSuccess }: Props) {
  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    if (!relatorio) return;
    setLoading(true);
    try {
      await excluirRelatorio(relatorio.id);
      message.success('Relatório excluído com sucesso');
      onSuccess();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      message.error(detail || 'Erro ao excluir relatório');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title="Confirmar Exclusão"
      open={open}
      onCancel={onClose}
      onOk={handleConfirm}
      okText="Confirmar Exclusão"
      okButtonProps={{ danger: true, loading }}
      cancelText="Cancelar"
    >
      {relatorio && (
        <div>
          <p>Tem certeza que deseja excluir este relatório?</p>
          <ul>
            <li><strong>Cliente:</strong> {relatorio.cliente_nome}</li>
            <li><strong>Período:</strong> {dayjs(relatorio.data_inicial).format('DD/MM/YYYY')} a {dayjs(relatorio.data_final).format('DD/MM/YYYY')}</li>
            <li><strong>Área Total:</strong> {Number(relatorio.total_area).toFixed(2)} ha</li>
            <li><strong>Missões:</strong> {relatorio.qtd_missoes}</li>
          </ul>
          <p style={{ color: '#faad14' }}>
            As missões vinculadas voltarão a ser elegíveis para novos relatórios.
          </p>
        </div>
      )}
    </Modal>
  );
}
