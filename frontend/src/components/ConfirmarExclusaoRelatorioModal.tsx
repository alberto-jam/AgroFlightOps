import { Alert, Checkbox, Modal, message } from 'antd';
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
  const [enviarCancelamento, setEnviarCancelamento] = useState(false);

  // Determine if this is an "already sent" report (informative mode)
  const isEnviado = relatorio?.status === 'ENVIADO' || !!relatorio?.enviado_em;

  const handleConfirm = async () => {
    if (!relatorio) return;
    setLoading(true);
    try {
      await excluirRelatorio(
        relatorio.id,
        isEnviado ? { enviar_cancelamento: enviarCancelamento } : undefined,
      );
      message.success('Relatório excluído com sucesso');
      onSuccess();
    } catch (err: unknown) {
      const response = (err as { response?: { status?: number; data?: { detail?: string } } })?.response;
      if (response?.status === 502) {
        handleForceDeleteConfirmation();
      } else {
        const detail = response?.data?.detail;
        message.error(detail || 'Erro ao excluir relatório');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleForceDeleteConfirmation = () => {
    Modal.confirm({
      title: 'Falha no envio do e-mail',
      content: 'O e-mail de cancelamento não pôde ser enviado. Deseja prosseguir com a exclusão mesmo assim?',
      okText: 'Sim, excluir mesmo assim',
      okButtonProps: { danger: true },
      cancelText: 'Cancelar',
      onOk: async () => {
        if (!relatorio) return;
        try {
          await excluirRelatorio(relatorio.id, { forcar_exclusao: true });
          message.success('Relatório excluído com sucesso');
          onSuccess();
        } catch {
          message.error('Erro ao excluir relatório');
        }
      },
    });
  };

  const handleClose = () => {
    setEnviarCancelamento(false);
    onClose();
  };

  return (
    <Modal
      title="Confirmar Exclusão"
      open={open}
      onCancel={handleClose}
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

          {isEnviado && (
            <div style={{ marginTop: 16 }}>
              <Alert
                type="warning"
                showIcon
                message="Este relatório já foi enviado ao cliente"
                description={
                  <div>
                    <p><strong>Data do envio:</strong> {relatorio.enviado_em ? dayjs(relatorio.enviado_em).format('DD/MM/YYYY HH:mm') : '-'}</p>
                    <p><strong>Destinatários:</strong> {relatorio.enviado_para || '-'}</p>
                  </div>
                }
                style={{ marginBottom: 16 }}
              />
              <Checkbox
                checked={enviarCancelamento}
                onChange={(e) => setEnviarCancelamento(e.target.checked)}
              >
                Enviar e-mail ao cliente informando o cancelamento do relatório
              </Checkbox>
            </div>
          )}

          <p style={{ color: '#faad14', marginTop: 16 }}>
            As missões vinculadas voltarão a ser elegíveis para novos relatórios.
          </p>
        </div>
      )}
    </Modal>
  );
}
