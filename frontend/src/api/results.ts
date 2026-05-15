import client from './client'

/**
 * 结果数据项
 */
export interface ResultItem {
  id: string
  taskId: string
  data: Record<string, any>
  sourceUrl: string
  extractedAt: string
}

/**
 * 分页参数
 */
export interface PaginationParams {
  page: number
  pageSize: number
}

/**
 * 分页元数据
 */
export interface PaginationMeta {
  page: number
  pageSize: number
  total: number
  totalPages: number
  hasNextPage: boolean
  hasPreviousPage: boolean
}

/**
 * 分页响应
 */
export interface PaginatedResponse<T> {
  data: T[]
  meta: PaginationMeta
}

/**
 * 计算总页数
 * @param total 总项目数
 * @param pageSize 每页项目数
 * @returns 总页数
 */
export function calculateTotalPages(total: number, pageSize: number): number {
  if (pageSize <= 0) {
    throw new Error('Page size must be greater than 0')
  }
  return Math.ceil(total / pageSize)
}

/**
 * 计算当前页的项目数
 * @param page 当前页码（从 1 开始）
 * @param pageSize 每页项目数
 * @param total 总项目数
 * @returns 当前页的项目数
 */
export function calculatePageItemCount(page: number, pageSize: number, total: number): number {
  if (page < 1) {
    throw new Error('Page must be >= 1')
  }
  if (pageSize <= 0) {
    throw new Error('Page size must be greater than 0')
  }
  if (total < 0) {
    throw new Error('Total must be >= 0')
  }

  const totalPages = calculateTotalPages(total, pageSize)
  if (page > totalPages) {
    return 0
  }

  const startIndex = (page - 1) * pageSize
  const endIndex = Math.min(startIndex + pageSize, total)
  return endIndex - startIndex
}

/**
 * 验证分页参数
 * @param page 页码
 * @param pageSize 每页项目数
 * @param total 总项目数
 * @returns 是否有效
 */
export function isValidPaginationParams(page: number, pageSize: number, total: number): boolean {
  if (page < 1 || pageSize <= 0 || total < 0) {
    return false
  }
  
  // 如果 total 为 0，则没有有效的页码
  if (total === 0) {
    return false
  }
  
  const totalPages = calculateTotalPages(total, pageSize)
  return page <= totalPages
}

/**
 * 从数据集中提取分页数据
 * @param data 完整数据集
 * @param page 页码（从 1 开始）
 * @param pageSize 每页项目数
 * @returns 分页后的数据
 */
export function paginateData<T>(data: T[], page: number, pageSize: number): T[] {
  if (page < 1) {
    throw new Error('Page must be >= 1')
  }
  if (pageSize <= 0) {
    throw new Error('Page size must be greater than 0')
  }

  const startIndex = (page - 1) * pageSize
  const endIndex = startIndex + pageSize
  return data.slice(startIndex, endIndex)
}

/**
 * 结果 API
 */
export const resultsAPI = {
  /**
   * 获取任务结果（分页）
   */
  getResults: (taskId: string, params: PaginationParams) => {
    return client.get<PaginatedResponse<ResultItem>>(`/api/v1/tasks/${taskId}/results`, {
      params,
    })
  },

  /**
   * 获取单个结果详情
   */
  getResult: (taskId: string, resultId: string) => {
    return client.get<ResultItem>(`/api/v1/tasks/${taskId}/results/${resultId}`)
  },

  /**
   * 搜索结果
   */
  searchResults: (taskId: string, query: string, params: PaginationParams) => {
    return client.get<PaginatedResponse<ResultItem>>(`/api/v1/tasks/${taskId}/results/search`, {
      params: { q: query, ...params },
    })
  },

  /**
   * 导出结果
   */
  exportResults: (taskId: string, format: 'csv' | 'json' | 'excel', params?: Record<string, any>) => {
    return client.post(`/api/v1/tasks/${taskId}/results/export`, {
      format,
      ...params,
    })
  },
}
