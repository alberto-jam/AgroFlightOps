/** Types for Gestão de Relatórios de Medição. */

export interface RelatorioMedicaoListItem {
  id: number;
  cliente_nome: string;
  data_inicial: string;
  data_final: string;
  total_area: number;
  qtd_missoes: number;
  gerado_em: string;
  status: string;
  enviado_em: string | null;
}

export interface RelatorioDownloadResponse {
  download_url: string;
}

export interface EnviarRelatorioRequest {
  emails: string[];
  mensagem?: string | null;
}

export interface EnviarRelatorioResponse {
  mensagem: string;
}

export interface ExcluirRelatorioResponse {
  mensagem: string;
}
