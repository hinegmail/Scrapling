import client from './client'

/**
 * 任务配置类型定义
 */
export interface TaskConfig {
  name: string
  description?: string
  targetUrl: string
  fetcherType: 'http' | 'dynamic' | 'stealthy'
  selector: string
  selectorType: 'css' | 'xpath'
  timeout?: number
  retryCount?: number
  useProxyRotation?: boolean
  solveCloudflare?: boolean
  customHeaders?: Record<string, string>
  cookies?: Record<string, string>
  waitTime?: number
  viewportWidth?: number
  viewportHeight?: number
}

/**
 * 任务类型定义
 */
export interface Task extends TaskConfig {
  id: string
  userId: string
  status: 'draft' | 'running' | 'paused' | 'completed' | 'failed' | 'stopped'
  createdAt: string
  updatedAt: string
  lastRunAt?: string
  totalRuns: number
  successCount: number
  errorCount: number
}

/**
 * 任务列表过滤条件
 */
export interface TaskFilterCriteria {
  status?: 'draft' | 'running' | 'paused' | 'completed' | 'failed' | 'stopped'
  startDate?: string // ISO 8601 格式
  endDate?: string // ISO 8601 格式
  keyword?: string // 搜索任务名称
}

/**
 * 任务列表过滤结果
 */
export interface FilteredTasksResult {
  tasks: Task[]
  total: number
  page: number
  pageSize: number
}

/**
 * 任务配置验证错误
 */
export interface ValidationError {
  field: string
  message: string
}

/**
 * 任务配置验证结果
 */
export interface ValidationResult {
  isValid: boolean
  errors: ValidationError[]
}

/**
 * 验证任务配置
 * @param config 任务配置对象
 * @returns 验证结果
 */
export function validateTaskConfig(config: Partial<TaskConfig>): ValidationResult {
  const errors: ValidationError[] = []

  // 验证必填字段
  if (!config.name || config.name.trim() === '') {
    errors.push({
      field: 'name',
      message: '任务名称是必填项',
    })
  }

  if (!config.targetUrl || config.targetUrl.trim() === '') {
    errors.push({
      field: 'targetUrl',
      message: '目标 URL 是必填项',
    })
  } else if (!isValidUrl(config.targetUrl)) {
    errors.push({
      field: 'targetUrl',
      message: '目标 URL 格式无效',
    })
  }

  if (!config.fetcherType) {
    errors.push({
      field: 'fetcherType',
      message: '获取器类型是必填项',
    })
  } else if (!['http', 'dynamic', 'stealthy'].includes(config.fetcherType)) {
    errors.push({
      field: 'fetcherType',
      message: '获取器类型无效',
    })
  }

  if (!config.selector || config.selector.trim() === '') {
    errors.push({
      field: 'selector',
      message: '选择器是必填项',
    })
  }

  if (!config.selectorType) {
    errors.push({
      field: 'selectorType',
      message: '选择器类型是必填项',
    })
  } else if (!['css', 'xpath'].includes(config.selectorType)) {
    errors.push({
      field: 'selectorType',
      message: '选择器类型无效',
    })
  }

  // 验证可选字段
  if (config.timeout !== undefined && config.timeout !== null) {
    if (!Number.isInteger(config.timeout) || config.timeout <= 0) {
      errors.push({
        field: 'timeout',
        message: '超时时间必须是正整数',
      })
    }
  }

  if (config.retryCount !== undefined && config.retryCount !== null) {
    if (!Number.isInteger(config.retryCount) || config.retryCount < 0) {
      errors.push({
        field: 'retryCount',
        message: '重试次数必须是非负整数',
      })
    }
  }

  if (config.waitTime !== undefined && config.waitTime !== null) {
    if (!Number.isInteger(config.waitTime) || config.waitTime < 0) {
      errors.push({
        field: 'waitTime',
        message: '等待时间必须是非负整数',
      })
    }
  }

  if (config.viewportWidth !== undefined && config.viewportWidth !== null) {
    if (!Number.isInteger(config.viewportWidth) || config.viewportWidth <= 0) {
      errors.push({
        field: 'viewportWidth',
        message: '视口宽度必须是正整数',
      })
    }
  }

  if (config.viewportHeight !== undefined && config.viewportHeight !== null) {
    if (!Number.isInteger(config.viewportHeight) || config.viewportHeight <= 0) {
      errors.push({
        field: 'viewportHeight',
        message: '视口高度必须是正整数',
      })
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  }
}

/**
 * 验证 URL 格式
 * @param url URL 字符串
 * @returns 是否有效
 */
function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 任务 API
 */
export const tasksAPI = {
  /**
   * 创建任务
   */
  createTask: (config: TaskConfig) => {
    return client.post('/api/v1/tasks', config)
  },

  /**
   * 获取任务列表
   */
  getTasks: (params?: { page?: number; pageSize?: number; status?: string }) => {
    return client.get('/api/v1/tasks', { params })
  },

  /**
   * 获取任务详情
   */
  getTask: (taskId: string) => {
    return client.get(`/api/v1/tasks/${taskId}`)
  },

  /**
   * 更新任务
   */
  updateTask: (taskId: string, config: Partial<TaskConfig>) => {
    return client.put(`/api/v1/tasks/${taskId}`, config)
  },

  /**
   * 删除任务
   */
  deleteTask: (taskId: string) => {
    return client.delete(`/api/v1/tasks/${taskId}`)
  },

  /**
   * 运行任务
   */
  runTask: (taskId: string) => {
    return client.post(`/api/v1/tasks/${taskId}/run`)
  },

  /**
   * 暂停任务
   */
  pauseTask: (taskId: string) => {
    return client.post(`/api/v1/tasks/${taskId}/pause`)
  },

  /**
   * 恢复任务
   */
  resumeTask: (taskId: string) => {
    return client.post(`/api/v1/tasks/${taskId}/resume`)
  },

  /**
   * 停止任务
   */
  stopTask: (taskId: string) => {
    return client.post(`/api/v1/tasks/${taskId}/stop`)
  },

  /**
   * 克隆任务
   */
  cloneTask: (taskId: string) => {
    return client.post(`/api/v1/tasks/${taskId}/clone`)
  },
}

/**
 * 过滤任务列表
 * 
 * 对于任何任务列表和过滤条件（状态、日期范围、关键词），
 * 过滤结果应该只包含与所有过滤条件匹配的任务。
 * 
 * @param tasks 任务列表
 * @param criteria 过滤条件
 * @returns 过滤后的任务列表
 */
export function filterTasks(tasks: Task[], criteria: TaskFilterCriteria): Task[] {
  return tasks.filter((task) => {
    // 按状态过滤
    if (criteria.status && task.status !== criteria.status) {
      return false
    }

    // 按日期范围过滤
    if (criteria.startDate) {
      const startDate = new Date(criteria.startDate)
      const taskDate = new Date(task.createdAt)
      if (taskDate < startDate) {
        return false
      }
    }

    if (criteria.endDate) {
      const endDate = new Date(criteria.endDate)
      const taskDate = new Date(task.createdAt)
      if (taskDate > endDate) {
        return false
      }
    }

    // 按关键词过滤（搜索任务名称）
    if (criteria.keyword) {
      const keyword = criteria.keyword.toLowerCase()
      if (!task.name.toLowerCase().includes(keyword)) {
        return false
      }
    }

    return true
  })
}
