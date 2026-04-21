import { useState, useEffect, useCallback, type ReactNode } from 'react';
import { Table, Input, Space } from 'antd';
import type { TableProps } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { SearchOutlined } from '@ant-design/icons';
import apiClient from '../api/client';
import type { PaginatedResponse } from '../types/common';

// Re-export for backward compatibility
export type { PaginatedResponse } from '../types/common';

export interface DataTableProps<T extends object> {
  /** Ant Design column definitions. */
  columns: ColumnsType<T>;
  /** API URL for server-side data fetching. Mutually exclusive with `dataSource`. */
  apiUrl?: string;
  /** Static data source. Mutually exclusive with `apiUrl`. */
  dataSource?: T[];
  /** Unique key field on each row. */
  rowKey: string | ((record: T) => string | number);
  /** Extra query params sent alongside page/page_size. */
  extraParams?: Record<string, unknown>;
  /** Show a global search input above the table. */
  showSearch?: boolean;
  /** Placeholder for the search input. */
  searchPlaceholder?: string;
  /** Query param name used for the search term (default `search`). */
  searchParamName?: string;
  /** Additional toolbar rendered to the right of the search input. */
  toolbar?: ReactNode;
  /** Default page size (default 20). */
  defaultPageSize?: number;
  /** Callback after data is fetched (useful for parent state sync). */
  onDataLoaded?: (data: PaginatedResponse<T>) => void;
  /** External trigger to refetch data — increment to refetch. */
  refreshKey?: number;
}

export default function DataTable<T extends object>({
  columns,
  apiUrl,
  dataSource,
  rowKey,
  extraParams,
  showSearch = false,
  searchPlaceholder = 'Pesquisar…',
  searchParamName = 'search',
  toolbar,
  defaultPageSize = 20,
  onDataLoaded,
  refreshKey,
}: DataTableProps<T>) {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(defaultPageSize);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');

  const fetchData = useCallback(async () => {
    if (!apiUrl) return;
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        page,
        page_size: pageSize,
        ...extraParams,
      };
      if (search) {
        params[searchParamName] = search;
      }
      const { data: res } = await apiClient.get<PaginatedResponse<T>>(apiUrl, { params });
      setData(res.items);
      setTotal(res.total);
      onDataLoaded?.(res);
    } catch {
      // errors are handled globally by the axios interceptor
    } finally {
      setLoading(false);
    }
  }, [apiUrl, page, pageSize, search, searchParamName, extraParams, onDataLoaded]);

  // Fetch when deps change
  useEffect(() => {
    if (apiUrl) {
      fetchData();
    }
  }, [fetchData, refreshKey]);

  // When using static dataSource, just mirror it
  useEffect(() => {
    if (dataSource) {
      setData(dataSource);
      setTotal(dataSource.length);
    }
  }, [dataSource]);

  const handleTableChange: TableProps<T>['onChange'] = (pagination) => {
    setPage(pagination.current ?? 1);
    setPageSize(pagination.pageSize ?? defaultPageSize);
  };

  return (
    <div>
      {(showSearch || toolbar) && (
        <Space style={{ marginBottom: 16, width: '100%', justifyContent: 'space-between' }} align="center">
          {showSearch ? (
            <Input
              prefix={<SearchOutlined />}
              placeholder={searchPlaceholder}
              allowClear
              style={{ width: 300 }}
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          ) : (
            <span />
          )}
          {toolbar && <div>{toolbar}</div>}
        </Space>
      )}

      <Table<T>
        columns={columns}
        dataSource={data}
        rowKey={rowKey}
        loading={loading}
        onChange={handleTableChange}
        pagination={
          apiUrl
            ? {
                current: page,
                pageSize,
                total,
                showSizeChanger: true,
                pageSizeOptions: ['10', '20', '50', '100'],
                showTotal: (t, range) => `${range[0]}-${range[1]} de ${t} registros`,
              }
            : {
                pageSize,
                showSizeChanger: true,
                pageSizeOptions: ['10', '20', '50', '100'],
                showTotal: (t, range) => `${range[0]}-${range[1]} de ${t} registros`,
              }
        }
      />
    </div>
  );
}
