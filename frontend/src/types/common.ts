/** Generic paginated response matching backend PaginatedResponse schema. */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
