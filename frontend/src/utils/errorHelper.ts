/**
 * Extrai a mensagem de detalhe de um erro de API (Axios).
 */
export function getApiErrorDetail(err: unknown): string | undefined {
  const axiosErr = err as { response?: { data?: { detail?: string }; status?: number } };
  return axiosErr?.response?.data?.detail;
}

export function getApiErrorStatus(err: unknown): number | undefined {
  const axiosErr = err as { response?: { status?: number } };
  return axiosErr?.response?.status;
}
