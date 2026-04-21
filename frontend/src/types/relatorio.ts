/** TypeScript interfaces for report types matching Pydantic schemas. */

export interface RelatorioFiltro {
  data_inicio: string;
  data_fim: string;
}

export interface MissoesPorStatusItem {
  status: string;
  total: number;
}

export interface MissoesPorStatusResponse {
  data_inicio: string;
  data_fim: string;
  items: MissoesPorStatusItem[];
  total_geral: number;
}

export interface AreaPorClienteItem {
  cliente_id: number;
  cliente_nome: string;
  area_total_pulverizada: number;
}

export interface AreaPorClienteResponse {
  data_inicio: string;
  data_fim: string;
  items: AreaPorClienteItem[];
}

export interface FinanceiroResumoResponse {
  data_inicio: string;
  data_fim: string;
  total_custo_estimado: number;
  total_custo_realizado: number;
  total_valor_faturado: number;
  total_missoes: number;
}

export interface UtilizacaoDroneItem {
  drone_id: number;
  drone_identificacao: string;
  drone_modelo: string;
  horas_voadas_periodo: number;
  total_missoes: number;
}

export interface UtilizacaoDroneResponse {
  data_inicio: string;
  data_fim: string;
  items: UtilizacaoDroneItem[];
}
