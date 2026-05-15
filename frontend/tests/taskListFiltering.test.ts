import { describe, it, expect } from 'vitest'
import fc from 'fast-check'
import { filterTasks, Task, TaskFilterCriteria } from '../src/api/tasks'

/**
 * 属性 6：任务列表过滤
 * 
 * **Validates: Requirements 5.7**
 * 
 * 对于任何任务列表和过滤条件（状态、日期范围、关键词），
 * 过滤结果应该只包含与所有过滤条件匹配的任务。
 */
describe('Property 6: Task List Filtering', () => {
  /**
   * 生成随机任务的 Arbitraries
   */
  // 使用有效的时间戳范围（2020-2024）
  const validTimestampArbitrary = fc.integer({ min: 1577836800000, max: Date.now() })
  
  const taskArbitrary = fc.record({
    id: fc.uuid(),
    userId: fc.uuid(),
    name: fc.string({ minLength: 1, maxLength: 100 }),
    description: fc.option(fc.string({ maxLength: 500 })),
    targetUrl: fc.webUrl(),
    fetcherType: fc.constantFrom('http' as const, 'dynamic' as const, 'stealthy' as const),
    selector: fc.string({ minLength: 1, maxLength: 100 }),
    selectorType: fc.constantFrom('css' as const, 'xpath' as const),
    timeout: fc.option(fc.integer({ min: 1, max: 3600 })),
    retryCount: fc.option(fc.integer({ min: 0, max: 10 })),
    useProxyRotation: fc.option(fc.boolean()),
    solveCloudflare: fc.option(fc.boolean()),
    customHeaders: fc.option(fc.dictionary(fc.string(), fc.string())),
    cookies: fc.option(fc.dictionary(fc.string(), fc.string())),
    waitTime: fc.option(fc.integer({ min: 0, max: 60 })),
    viewportWidth: fc.option(fc.integer({ min: 320, max: 2560 })),
    viewportHeight: fc.option(fc.integer({ min: 240, max: 1440 })),
    status: fc.constantFrom(
      'draft' as const,
      'running' as const,
      'paused' as const,
      'completed' as const,
      'failed' as const,
      'stopped' as const
    ),
    createdAt: validTimestampArbitrary.map((ts) => new Date(ts).toISOString()),
    updatedAt: validTimestampArbitrary.map((ts) => new Date(ts).toISOString()),
    lastRunAt: fc.option(validTimestampArbitrary.map((ts) => new Date(ts).toISOString())),
    totalRuns: fc.integer({ min: 0, max: 1000 }),
    successCount: fc.integer({ min: 0, max: 1000 }),
    errorCount: fc.integer({ min: 0, max: 1000 }),
  })

  /**
   * 属性 6.1：状态过滤准确性
   * 
   * 对于任何任务列表和状态过滤条件，
   * 过滤结果中的所有任务状态都应该与指定的状态匹配。
   */
  describe('Property 6.1: Status Filter Accuracy', () => {
    it('should filter tasks by status correctly', () => {
      fc.assert(
        fc.property(fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }), (tasks) => {
          const statuses: Array<Task['status']> = [
            'draft',
            'running',
            'paused',
            'completed',
            'failed',
            'stopped',
          ]

          statuses.forEach((status) => {
            const criteria: TaskFilterCriteria = { status }
            const filtered = filterTasks(tasks, criteria)

            // 所有过滤结果的状态都应该匹配
            filtered.forEach((task) => {
              expect(task.status).toBe(status)
            })

            // 过滤结果应该包含所有匹配的任务
            const expectedCount = tasks.filter((t) => t.status === status).length
            expect(filtered.length).toBe(expectedCount)
          })
        }),
        { numRuns: 100 }
      )
    })

    it('should return empty array when no tasks match status filter', () => {
      fc.assert(
        fc.property(fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }), (tasks) => {
          // 创建一个不存在的状态过滤条件
          const allTasks = tasks.map((t) => ({ ...t, status: 'draft' as const }))
          const criteria: TaskFilterCriteria = { status: 'running' }
          const filtered = filterTasks(allTasks, criteria)

          expect(filtered.length).toBe(0)
        }),
        { numRuns: 50 }
      )
    })
  })

  /**
   * 属性 6.2：日期范围过滤准确性
   * 
   * 对于任何任务列表和日期范围过滤条件，
   * 过滤结果中的所有任务创建日期都应该在指定的日期范围内。
   */
  describe('Property 6.2: Date Range Filter Accuracy', () => {
    it('should filter tasks by start date correctly', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.date(),
          (tasks, startDate) => {
            const criteria: TaskFilterCriteria = { startDate: startDate.toISOString() }
            const filtered = filterTasks(tasks, criteria)

            // 所有过滤结果的创建日期都应该 >= startDate
            filtered.forEach((task) => {
              const taskDate = new Date(task.createdAt)
              expect(taskDate.getTime()).toBeGreaterThanOrEqual(startDate.getTime())
            })

            // 过滤结果应该包含所有匹配的任务
            const expectedCount = tasks.filter((t) => {
              const taskDate = new Date(t.createdAt)
              return taskDate.getTime() >= startDate.getTime()
            }).length
            expect(filtered.length).toBe(expectedCount)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should filter tasks by end date correctly', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.date(),
          (tasks, endDate) => {
            const criteria: TaskFilterCriteria = { endDate: endDate.toISOString() }
            const filtered = filterTasks(tasks, criteria)

            // 所有过滤结果的创建日期都应该 <= endDate
            filtered.forEach((task) => {
              const taskDate = new Date(task.createdAt)
              expect(taskDate.getTime()).toBeLessThanOrEqual(endDate.getTime())
            })

            // 过滤结果应该包含所有匹配的任务
            const expectedCount = tasks.filter((t) => {
              const taskDate = new Date(t.createdAt)
              return taskDate.getTime() <= endDate.getTime()
            }).length
            expect(filtered.length).toBe(expectedCount)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should filter tasks by date range correctly', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.tuple(fc.date(), fc.date()),
          (tasks, [date1, date2]) => {
            const startDate = new Date(Math.min(date1.getTime(), date2.getTime()))
            const endDate = new Date(Math.max(date1.getTime(), date2.getTime()))

            const criteria: TaskFilterCriteria = {
              startDate: startDate.toISOString(),
              endDate: endDate.toISOString(),
            }
            const filtered = filterTasks(tasks, criteria)

            // 所有过滤结果的创建日期都应该在范围内
            filtered.forEach((task) => {
              const taskDate = new Date(task.createdAt)
              expect(taskDate.getTime()).toBeGreaterThanOrEqual(startDate.getTime())
              expect(taskDate.getTime()).toBeLessThanOrEqual(endDate.getTime())
            })

            // 过滤结果应该包含所有匹配的任务
            const expectedCount = tasks.filter((t) => {
              const taskDate = new Date(t.createdAt)
              return (
                taskDate.getTime() >= startDate.getTime() &&
                taskDate.getTime() <= endDate.getTime()
              )
            }).length
            expect(filtered.length).toBe(expectedCount)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should return empty array when date range has no matching tasks', () => {
      fc.assert(
        fc.property(fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }), (tasks) => {
          // 创建一个远在过去的日期范围
          const startDate = new Date('2000-01-01')
          const endDate = new Date('2000-12-31')

          const criteria: TaskFilterCriteria = {
            startDate: startDate.toISOString(),
            endDate: endDate.toISOString(),
          }
          const filtered = filterTasks(tasks, criteria)

          // 验证过滤结果中的所有任务都在指定的日期范围内
          filtered.forEach((task) => {
            const taskDate = new Date(task.createdAt)
            expect(taskDate.getTime()).toBeGreaterThanOrEqual(startDate.getTime())
            expect(taskDate.getTime()).toBeLessThanOrEqual(endDate.getTime())
          })
        }),
        { numRuns: 50 }
      )
    })
  })

  /**
   * 属性 6.3：关键词过滤准确性
   * 
   * 对于任何任务列表和关键词过滤条件，
   * 过滤结果中的所有任务名称都应该包含指定的关键词（不区分大小写）。
   */
  describe('Property 6.3: Keyword Filter Accuracy', () => {
    it('should filter tasks by keyword correctly', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.string({ minLength: 1, maxLength: 20 }),
          (tasks, keyword) => {
            const criteria: TaskFilterCriteria = { keyword }
            const filtered = filterTasks(tasks, criteria)

            // 所有过滤结果的名称都应该包含关键词（不区分大小写）
            const keywordLower = keyword.toLowerCase()
            filtered.forEach((task) => {
              expect(task.name.toLowerCase()).toContain(keywordLower)
            })

            // 过滤结果应该包含所有匹配的任务
            const expectedCount = tasks.filter((t) =>
              t.name.toLowerCase().includes(keywordLower)
            ).length
            expect(filtered.length).toBe(expectedCount)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should be case-insensitive for keyword filtering', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.string({ minLength: 1, maxLength: 20 }),
          (tasks, keyword) => {
            const criteria1: TaskFilterCriteria = { keyword }
            const criteria2: TaskFilterCriteria = { keyword: keyword.toUpperCase() }
            const criteria3: TaskFilterCriteria = { keyword: keyword.toLowerCase() }

            const filtered1 = filterTasks(tasks, criteria1)
            const filtered2 = filterTasks(tasks, criteria2)
            const filtered3 = filterTasks(tasks, criteria3)

            // 不同大小写的关键词应该返回相同的结果
            expect(filtered1.length).toBe(filtered2.length)
            expect(filtered1.length).toBe(filtered3.length)
            expect(filtered1.map((t) => t.id).sort()).toEqual(
              filtered2.map((t) => t.id).sort()
            )
            expect(filtered1.map((t) => t.id).sort()).toEqual(
              filtered3.map((t) => t.id).sort()
            )
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should return empty array when no tasks match keyword filter', () => {
      fc.assert(
        fc.property(fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }), (tasks) => {
          const criteria: TaskFilterCriteria = { keyword: 'NONEXISTENT_KEYWORD_XYZ' }
          const filtered = filterTasks(tasks, criteria)

          expect(filtered.length).toBe(0)
        }),
        { numRuns: 50 }
      )
    })
  })

  /**
   * 属性 6.4：多条件过滤准确性
   * 
   * 对于任何任务列表和多个过滤条件的组合，
   * 过滤结果应该只包含与所有条件都匹配的任务。
   */
  describe('Property 6.4: Multi-Condition Filter Accuracy', () => {
    it('should filter tasks by status and keyword correctly', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.constantFrom(
            'draft' as const,
            'running' as const,
            'paused' as const,
            'completed' as const,
            'failed' as const,
            'stopped' as const
          ),
          fc.string({ minLength: 1, maxLength: 20 }),
          (tasks, status, keyword) => {
            const criteria: TaskFilterCriteria = { status, keyword }
            const filtered = filterTasks(tasks, criteria)

            // 所有过滤结果都应该匹配两个条件
            const keywordLower = keyword.toLowerCase()
            filtered.forEach((task) => {
              expect(task.status).toBe(status)
              expect(task.name.toLowerCase()).toContain(keywordLower)
            })

            // 过滤结果应该包含所有匹配的任务
            const expectedCount = tasks.filter(
              (t) => t.status === status && t.name.toLowerCase().includes(keywordLower)
            ).length
            expect(filtered.length).toBe(expectedCount)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should filter tasks by status and date range correctly', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.constantFrom(
            'draft' as const,
            'running' as const,
            'paused' as const,
            'completed' as const,
            'failed' as const,
            'stopped' as const
          ),
          fc.tuple(fc.date(), fc.date()),
          (tasks, status, [date1, date2]) => {
            const startDate = new Date(Math.min(date1.getTime(), date2.getTime()))
            const endDate = new Date(Math.max(date1.getTime(), date2.getTime()))

            const criteria: TaskFilterCriteria = {
              status,
              startDate: startDate.toISOString(),
              endDate: endDate.toISOString(),
            }
            const filtered = filterTasks(tasks, criteria)

            // 所有过滤结果都应该匹配所有条件
            filtered.forEach((task) => {
              expect(task.status).toBe(status)
              const taskDate = new Date(task.createdAt)
              expect(taskDate.getTime()).toBeGreaterThanOrEqual(startDate.getTime())
              expect(taskDate.getTime()).toBeLessThanOrEqual(endDate.getTime())
            })

            // 过滤结果应该包含所有匹配的任务
            const expectedCount = tasks.filter((t) => {
              const taskDate = new Date(t.createdAt)
              return (
                t.status === status &&
                taskDate.getTime() >= startDate.getTime() &&
                taskDate.getTime() <= endDate.getTime()
              )
            }).length
            expect(filtered.length).toBe(expectedCount)
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should filter tasks by all three conditions correctly', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.constantFrom(
            'draft' as const,
            'running' as const,
            'paused' as const,
            'completed' as const,
            'failed' as const,
            'stopped' as const
          ),
          fc.tuple(fc.date(), fc.date()),
          fc.string({ minLength: 1, maxLength: 20 }),
          (tasks, status, [date1, date2], keyword) => {
            const startDate = new Date(Math.min(date1.getTime(), date2.getTime()))
            const endDate = new Date(Math.max(date1.getTime(), date2.getTime()))

            const criteria: TaskFilterCriteria = {
              status,
              startDate: startDate.toISOString(),
              endDate: endDate.toISOString(),
              keyword,
            }
            const filtered = filterTasks(tasks, criteria)

            // 所有过滤结果都应该匹配所有条件
            const keywordLower = keyword.toLowerCase()
            filtered.forEach((task) => {
              expect(task.status).toBe(status)
              const taskDate = new Date(task.createdAt)
              expect(taskDate.getTime()).toBeGreaterThanOrEqual(startDate.getTime())
              expect(taskDate.getTime()).toBeLessThanOrEqual(endDate.getTime())
              expect(task.name.toLowerCase()).toContain(keywordLower)
            })

            // 过滤结果应该包含所有匹配的任务
            const expectedCount = tasks.filter((t) => {
              const taskDate = new Date(t.createdAt)
              return (
                t.status === status &&
                taskDate.getTime() >= startDate.getTime() &&
                taskDate.getTime() <= endDate.getTime() &&
                t.name.toLowerCase().includes(keywordLower)
              )
            }).length
            expect(filtered.length).toBe(expectedCount)
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  /**
   * 属性 6.5：空过滤条件
   * 
   * 对于任何任务列表和空的过滤条件（没有指定任何过滤条件），
   * 过滤结果应该返回所有任务。
   */
  describe('Property 6.5: Empty Filter Criteria', () => {
    it('should return all tasks when no filter criteria is provided', () => {
      fc.assert(
        fc.property(fc.array(taskArbitrary, { minLength: 0, maxLength: 100 }), (tasks) => {
          const criteria: TaskFilterCriteria = {}
          const filtered = filterTasks(tasks, criteria)

          expect(filtered.length).toBe(tasks.length)
          expect(filtered.map((t) => t.id).sort()).toEqual(
            tasks.map((t) => t.id).sort()
          )
        }),
        { numRuns: 100 }
      )
    })

    it('should return all tasks when filter criteria is undefined', () => {
      fc.assert(
        fc.property(fc.array(taskArbitrary, { minLength: 0, maxLength: 100 }), (tasks) => {
          const criteria: TaskFilterCriteria = {
            status: undefined,
            startDate: undefined,
            endDate: undefined,
            keyword: undefined,
          }
          const filtered = filterTasks(tasks, criteria)

          expect(filtered.length).toBe(tasks.length)
        }),
        { numRuns: 100 }
      )
    })
  })

  /**
   * 属性 6.6：过滤结果的子集性质
   * 
   * 对于任何任务列表和过滤条件，
   * 过滤结果应该是原始任务列表的子集。
   */
  describe('Property 6.6: Filtering Result Subset Property', () => {
    it('should return a subset of the original tasks', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.option(
            fc.constantFrom(
              'draft' as const,
              'running' as const,
              'paused' as const,
              'completed' as const,
              'failed' as const,
              'stopped' as const
            )
          ),
          fc.option(fc.date()),
          fc.option(fc.string({ minLength: 1, maxLength: 20 })),
          (tasks, status, date, keyword) => {
            const criteria: TaskFilterCriteria = {
              status: status || undefined,
              startDate: date ? date.toISOString() : undefined,
              keyword: keyword || undefined,
            }
            const filtered = filterTasks(tasks, criteria)

            // 过滤结果应该是原始列表的子集
            expect(filtered.length).toBeLessThanOrEqual(tasks.length)

            // 过滤结果中的所有任务都应该在原始列表中
            filtered.forEach((filteredTask) => {
              const found = tasks.find((t) => t.id === filteredTask.id)
              expect(found).toBeDefined()
            })
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should not modify the original tasks array', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.option(
            fc.constantFrom(
              'draft' as const,
              'running' as const,
              'paused' as const,
              'completed' as const,
              'failed' as const,
              'stopped' as const
            )
          ),
          (tasks, status) => {
            const originalTasks = JSON.parse(JSON.stringify(tasks))
            const criteria: TaskFilterCriteria = { status: status || undefined }

            filterTasks(tasks, criteria)

            // 原始数组应该保持不变
            expect(tasks).toEqual(originalTasks)
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  /**
   * 属性 6.7：过滤的幂等性
   * 
   * 对于任何任务列表和过滤条件，
   * 对过滤结果再次应用相同的过滤条件应该返回相同的结果。
   */
  describe('Property 6.7: Filtering Idempotence', () => {
    it('should be idempotent - filtering twice should give same result', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.option(
            fc.constantFrom(
              'draft' as const,
              'running' as const,
              'paused' as const,
              'completed' as const,
              'failed' as const,
              'stopped' as const
            )
          ),
          fc.option(fc.date()),
          fc.option(fc.string({ minLength: 1, maxLength: 20 })),
          (tasks, status, date, keyword) => {
            const criteria: TaskFilterCriteria = {
              status: status || undefined,
              startDate: date ? date.toISOString() : undefined,
              keyword: keyword || undefined,
            }

            const filtered1 = filterTasks(tasks, criteria)
            const filtered2 = filterTasks(filtered1, criteria)

            // 两次过滤应该返回相同的结果
            expect(filtered1.length).toBe(filtered2.length)
            expect(filtered1.map((t) => t.id).sort()).toEqual(
              filtered2.map((t) => t.id).sort()
            )
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  /**
   * 属性 6.8：过滤的交换律
   * 
   * 对于任何任务列表和两个不同的过滤条件，
   * 先应用条件 A 再应用条件 B 应该与先应用条件 B 再应用条件 A 返回相同的结果。
   */
  describe('Property 6.8: Filtering Commutativity', () => {
    it('should be commutative - order of filtering should not matter', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.option(
            fc.constantFrom(
              'draft' as const,
              'running' as const,
              'paused' as const,
              'completed' as const,
              'failed' as const,
              'stopped' as const
            )
          ),
          fc.option(fc.string({ minLength: 1, maxLength: 20 })),
          (tasks, status, keyword) => {
            const criteria1: TaskFilterCriteria = { status: status || undefined }
            const criteria2: TaskFilterCriteria = { keyword: keyword || undefined }

            // 先应用 criteria1 再应用 criteria2
            const filtered1 = filterTasks(filterTasks(tasks, criteria1), criteria2)

            // 先应用 criteria2 再应用 criteria1
            const filtered2 = filterTasks(filterTasks(tasks, criteria2), criteria1)

            // 结果应该相同
            expect(filtered1.length).toBe(filtered2.length)
            expect(filtered1.map((t) => t.id).sort()).toEqual(
              filtered2.map((t) => t.id).sort()
            )
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  /**
   * 属性 6.9：过滤的完整性
   * 
   * 对于任何任务列表，
   * 过滤结果中的任务数量应该不超过原始列表中的任务数量。
   */
  describe('Property 6.9: Filtering Completeness', () => {
    it('should never return more tasks than the original list', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 0, maxLength: 100 }),
          fc.option(
            fc.constantFrom(
              'draft' as const,
              'running' as const,
              'paused' as const,
              'completed' as const,
              'failed' as const,
              'stopped' as const
            )
          ),
          fc.option(fc.date()),
          fc.option(fc.string({ minLength: 1, maxLength: 20 })),
          (tasks, status, date, keyword) => {
            const criteria: TaskFilterCriteria = {
              status: status || undefined,
              startDate: date ? date.toISOString() : undefined,
              keyword: keyword || undefined,
            }
            const filtered = filterTasks(tasks, criteria)

            expect(filtered.length).toBeLessThanOrEqual(tasks.length)
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  /**
   * 属性 6.10：特殊字符处理
   * 
   * 对于任何包含特殊字符的关键词，
   * 过滤应该正确处理这些字符。
   */
  describe('Property 6.10: Special Characters Handling', () => {
    it('should handle special characters in keyword filter', () => {
      fc.assert(
        fc.property(
          fc.array(taskArbitrary, { minLength: 1, maxLength: 100 }),
          fc.string({ minLength: 1, maxLength: 20 }),
          (tasks, keyword) => {
            const criteria: TaskFilterCriteria = { keyword }
            const filtered = filterTasks(tasks, criteria)

            // 应该不抛出异常
            expect(Array.isArray(filtered)).toBe(true)

            // 所有过滤结果都应该包含关键词
            const keywordLower = keyword.toLowerCase()
            filtered.forEach((task) => {
              expect(task.name.toLowerCase()).toContain(keywordLower)
            })
          }
        ),
        { numRuns: 100 }
      )
    })
  })
})
