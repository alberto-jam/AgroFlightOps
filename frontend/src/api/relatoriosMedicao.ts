import apiClient from './client';
import type { PaginatedResponse } from '../types/common';
import type {
  EnviarRelatorioRequest,
  EnviarRelatorioResponse,
  ExcluirRelatorioResponse,
  RelatorioDownloadResponse,
  RelatorioMedicaoListItem,
} from '../types/relatorio-medicao';

export interface ListarRelatoriosParams {
  cliente_id?: number;
  data_inicial?: string;
  data_final?: string;
  status?: string;
  page?: number;
  page_size?: number;
}

export async function listarRelatorios(
  params: ListarRelatoriosParams,
): Promise<PaginatedResponse<RelatorioMedicaoListItem>> {
  const { data } = await apiClient.get<PaginatedResponse<RelatorioMedicaoListItem>>(
    '/medicoes-rop/relatorios',
    { params },
  );
  return data;
}

export async function downloadRelatorio(id: number): Promise<RelatorioDownloadResponse> {
  const { data } = await apiClient.get<RelatorioDownloadResponse>(
    `/medicoes-rop/relatorios/${id}/download`,
  );
  return data;
}

export async function excluirRelatorio(id: number): Promise<ExcluirRelatorioResponse> {
  const { data } = await apiClient.delete<ExcluirRelatorioResponse>(
    `/medicoes-rop/relatorios/${id}`,
  );
  return data;
}

export async function enviarRelatorio(
  id: number,
  payload: EnviarRelatorioRequest,
): Promise<EnviarRelatorioResponse> {
  const { data } = await apiClient.post<EnviarRelatorioResponse>(
    `/medicoes-rop/relatorios/${id}/enviar`,
    payload,
  );
  return data;
}
