import { describe, it, expect } from 'vitest'
import {
  calculateTotalPages,
  calculatePageItemCount,
  isValidPaginationParams,
  paginateData,
  ResultItem,
} from '../src/api/results'

/**
 * 属性 4：结果表分页
 *
 * **Validates: Requirements 4.2**
 *
 * 对于任何包含 N 个项目和页面大小为 P 的结果数据集，分页应该正确地将结果分成 ceil(N/P) 页，
 * 每页包含恰好 min(P, remaining_items) 个结果。
 */
describe('Property 4: Results Table Pagination', () => {
  /**
   * 属性 4.1：总页数计算
   *
   * 对于任何总项目数 N 和页面大小 P（P > 0），
   * 计算的总页数应该等于 ceil(N/P)。
   */
  describe('Property 4.1: Total Pages Calculation', () => {
    it('should calculate correct total pages for exact division', () => {
      const testCases = [
        { total: 10, pageSize: 5, expected: 2 },
        { total: 20, pageSize: 10, expected: 2 },
        { total: 100, pageSize: 25, expected: 4 },
        { total: 1000, pageSize: 100, expected: 10 },
      ]

      testCases.forEach(({ total, pageSize, expected }) => {
        const result = calculateTotalPages(total, pageSize)
        expect(result).toBe(expected)
      })
    })

    it('should calculate correct total pages for non-exact division', () => {
      const testCases = [
        { total: 10, pageSize: 3, expected: 4 },
        { total: 20, pageSize: 7, expected: 3 },
        { total: 100, pageSize: 30, expected: 4 },
        { total: 1000, pageSize: 333, expected: 4 },
      ]

      testCases.forEach(({ total, pageSize, expected }) => {
        const result = calculateTotalPages(total, pageSize)
        expect(result).toBe(expected)
      })
    })

    it('should calculate correct total pages for single item', () => {
      const testCases = [
        { total: 1, pageSize: 1, expected: 1 },
        { total: 1, pageSize: 10, expected: 1 },
        { total: 1, pageSize: 100, expected: 1 },
      ]

      testCases.forEach(({ total, pageSize, expected }) => {
        const result = calculateTotalPages(total, pageSize)
        expect(result).toBe(expected)
      })
    })

    it('should calculate correct total pages for zero items', () => {
      const testCases = [
        { total: 0, pageSize: 1, expected: 0 },
        { total: 0, pageSize: 10, expected: 0 },
        { total: 0, pageSize: 100, expected: 0 },
      ]

      testCases.forEach(({ total, pageSize, expected }) => {
        const result = calculateTotalPages(total, pageSize)
        expect(result).toBe(expected)
      })
    })

    it('should throw error for invalid page size', () => {
      expect(() => calculateTotalPages(10, 0)).toThrow()
      expect(() => calculateTotalPages(10, -1)).toThrow()
    })

    it('should handle large numbers correctly', () => {
      const result = calculateTotalPages(1000000, 1000)
      expect(result).toBe(1000)

      const result2 = calculateTotalPages(1000001, 1000)
      expect(result2).toBe(1001)
    })
  })

  /**
   * 属性 4.2：每页项目数计算
   *
   * 对于任何页码 page（page >= 1）、页面大小 P（P > 0）和总项目数 N（N >= 0），
   * 当前页的项目数应该等于 min(P, N - (page - 1) * P)，
   * 如果 page > ceil(N/P)，则应该返回 0。
   */
  describe('Property 4.2: Page Item Count Calculation', () => {
    it('should calculate correct item count for full pages', () => {
      const testCases = [
        { page: 1, pageSize: 10, total: 100, expected: 10 },
        { page: 2, pageSize: 10, total: 100, expected: 10 },
        { page: 5, pageSize: 10, total: 100, expected: 10 },
        { page: 10, pageSize: 10, total: 100, expected: 10 },
      ]

      testCases.forEach(({ page, pageSize, total, expected }) => {
        const result = calculatePageItemCount(page, pageSize, total)
        expect(result).toBe(expected)
      })
    })

    it('should calculate correct item count for last partial page', () => {
      const testCases = [
        { page: 4, pageSize: 10, total: 35, expected: 5 },
        { page: 3, pageSize: 7, total: 20, expected: 6 },
        { page: 11, pageSize: 100, total: 1001, expected: 1 },
      ]

      testCases.forEach(({ page, pageSize, total, expected }) => {
        const result = calculatePageItemCount(page, pageSize, total)
        expect(result).toBe(expected)
      })
    })

    it('should return 0 for page beyond total pages', () => {
      const testCases = [
        { page: 11, pageSize: 10, total: 100 },
        { page: 100, pageSize: 10, total: 100 },
        { page: 5, pageSize: 10, total: 30 },
      ]

      testCases.forEach(({ page, pageSize, total }) => {
        const result = calculatePageItemCount(page, pageSize, total)
        expect(result).toBe(0)
      })
    })

    it('should handle single item correctly', () => {
      expect(calculatePageItemCount(1, 1, 1)).toBe(1)
      expect(calculatePageItemCount(1, 10, 1)).toBe(1)
      expect(calculatePageItemCount(2, 10, 1)).toBe(0)
    })

    it('should handle zero items correctly', () => {
      expect(calculatePageItemCount(1, 10, 0)).toBe(0)
      expect(calculatePageItemCount(2, 10, 0)).toBe(0)
    })

    it('should throw error for invalid page', () => {
      expect(() => calculatePageItemCount(0, 10, 100)).toThrow()
      expect(() => calculatePageItemCount(-1, 10, 100)).toThrow()
    })

    it('should throw error for invalid page size', () => {
      expect(() => calculatePageItemCount(1, 0, 100)).toThrow()
      expect(() => calculatePageItemCount(1, -1, 100)).toThrow()
    })

    it('should throw error for invalid total', () => {
      expect(() => calculatePageItemCount(1, 10, -1)).toThrow()
    })
  })

  /**
   * 属性 4.3：分页数据提取
   *
   * 对于任何数据集、页码和页面大小，
   * 提取的分页数据应该包含正确的项目数，
   * 且项目顺序应该与原始数据集一致。
   */
  describe('Property 4.3: Paginated Data Extraction', () => {
    it('should extract correct data for first page', () => {
      const data = Array.from({ length: 100 }, (_, i) => i + 1)
      const result = paginateData(data, 1, 10)

      expect(result).toHaveLength(10)
      expect(result).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    })

    it('should extract correct data for middle page', () => {
      const data = Array.from({ length: 100 }, (_, i) => i + 1)
      const result = paginateData(data, 5, 10)

      expect(result).toHaveLength(10)
      expect(result).toEqual([41, 42, 43, 44, 45, 46, 47, 48, 49, 50])
    })

    it('should extract correct data for last page', () => {
      const data = Array.from({ length: 100 }, (_, i) => i + 1)
      const result = paginateData(data, 10, 10)

      expect(result).toHaveLength(10)
      expect(result).toEqual([91, 92, 93, 94, 95, 96, 97, 98, 99, 100])
    })

    it('should extract correct data for partial last page', () => {
      const data = Array.from({ length: 35 }, (_, i) => i + 1)
      const result = paginateData(data, 4, 10)

      expect(result).toHaveLength(5)
      expect(result).toEqual([31, 32, 33, 34, 35])
    })

    it('should return empty array for page beyond data', () => {
      const data = Array.from({ length: 100 }, (_, i) => i + 1)
      const result = paginateData(data, 11, 10)

      expect(result).toHaveLength(0)
      expect(result).toEqual([])
    })

    it('should handle single item correctly', () => {
      const data = [1]
      const result = paginateData(data, 1, 1)

      expect(result).toHaveLength(1)
      expect(result).toEqual([1])
    })

    it('should handle empty data correctly', () => {
      const data: number[] = []
      const result = paginateData(data, 1, 10)

      expect(result).toHaveLength(0)
      expect(result).toEqual([])
    })

    it('should preserve data order', () => {
      const data = Array.from({ length: 50 }, (_, i) => ({ id: i, value: `item-${i}` }))
      const result = paginateData(data, 2, 10)

      expect(result).toHaveLength(10)
      expect(result[0].id).toBe(10)
      expect(result[9].id).toBe(19)
      result.forEach((item, index) => {
        expect(item.id).toBe(10 + index)
      })
    })

    it('should throw error for invalid page', () => {
      const data = Array.from({ length: 100 }, (_, i) => i + 1)
      expect(() => paginateData(data, 0, 10)).toThrow()
      expect(() => paginateData(data, -1, 10)).toThrow()
    })

    it('should throw error for invalid page size', () => {
      const data = Array.from({ length: 100 }, (_, i) => i + 1)
      expect(() => paginateData(data, 1, 0)).toThrow()
      expect(() => paginateData(data, 1, -1)).toThrow()
    })
  })

  /**
   * 属性 4.4：分页参数验证
   *
   * 对于任何页码、页面大小和总项目数，
   * 验证函数应该正确识别参数是否有效。
   */
  describe('Property 4.4: Pagination Parameters Validation', () => {
    it('should validate correct parameters', () => {
      const testCases = [
        { page: 1, pageSize: 10, total: 100, expected: true },
        { page: 5, pageSize: 10, total: 100, expected: true },
        { page: 10, pageSize: 10, total: 100, expected: true },
        { page: 1, pageSize: 1, total: 1, expected: true },
      ]

      testCases.forEach(({ page, pageSize, total, expected }) => {
        const result = isValidPaginationParams(page, pageSize, total)
        expect(result).toBe(expected)
      })
    })

    it('should reject invalid page', () => {
      expect(isValidPaginationParams(0, 10, 100)).toBe(false)
      expect(isValidPaginationParams(-1, 10, 100)).toBe(false)
      expect(isValidPaginationParams(11, 10, 100)).toBe(false)
    })

    it('should reject invalid page size', () => {
      expect(isValidPaginationParams(1, 0, 100)).toBe(false)
      expect(isValidPaginationParams(1, -1, 100)).toBe(false)
    })

    it('should reject invalid total', () => {
      expect(isValidPaginationParams(1, 10, -1)).toBe(false)
    })

    it('should handle edge cases', () => {
      expect(isValidPaginationParams(1, 10, 0)).toBe(false)
      expect(isValidPaginationParams(1, 1, 1)).toBe(true)
      expect(isValidPaginationParams(1, 1000000, 1000000)).toBe(true)
    })
  })

  /**
   * 属性 4.5：分页一致性
   *
   * 对于任何数据集、页码和页面大小，
   * 分页后的所有页面的项目总数应该等于原始数据集的大小。
   */
  describe('Property 4.5: Pagination Consistency', () => {
    it('should maintain total item count across all pages', () => {
      const testCases = [
        { total: 100, pageSize: 10 },
        { total: 100, pageSize: 7 },
        { total: 35, pageSize: 10 },
        { total: 1, pageSize: 1 },
        { total: 0, pageSize: 10 },
      ]

      testCases.forEach(({ total, pageSize }) => {
        const data = Array.from({ length: total }, (_, i) => i)
        const totalPages = calculateTotalPages(total, pageSize)

        let totalItems = 0
        for (let page = 1; page <= totalPages; page++) {
          const pageData = paginateData(data, page, pageSize)
          totalItems += pageData.length
        }

        expect(totalItems).toBe(total)
      })
    })

    it('should not lose or duplicate items across pages', () => {
      const data = Array.from({ length: 100 }, (_, i) => i)
      const pageSize = 7
      const totalPages = calculateTotalPages(100, pageSize)

      const allItems: number[] = []
      for (let page = 1; page <= totalPages; page++) {
        const pageData = paginateData(data, page, pageSize)
        allItems.push(...pageData)
      }

      expect(allItems).toHaveLength(100)
      expect(allItems).toEqual(data)
    })

    it('should handle non-exact division correctly', () => {
      const data = Array.from({ length: 35 }, (_, i) => i)
      const pageSize = 10
      const totalPages = calculateTotalPages(35, pageSize)

      expect(totalPages).toBe(4)

      const page1 = paginateData(data, 1, pageSize)
      const page2 = paginateData(data, 2, pageSize)
      const page3 = paginateData(data, 3, pageSize)
      const page4 = paginateData(data, 4, pageSize)

      expect(page1).toHaveLength(10)
      expect(page2).toHaveLength(10)
      expect(page3).toHaveLength(10)
      expect(page4).toHaveLength(5)

      const allItems = [...page1, ...page2, ...page3, ...page4]
      expect(allItems).toEqual(data)
    })
  })

  /**
   * 属性 4.6：分页边界条件
   *
   * 对于任何边界情况（空数据集、单个项目、大数据集），
   * 分页应该正确处理。
   */
  describe('Property 4.6: Pagination Boundary Conditions', () => {
    it('should handle empty dataset', () => {
      const data: number[] = []
      const totalPages = calculateTotalPages(0, 10)

      expect(totalPages).toBe(0)

      const result = paginateData(data, 1, 10)
      expect(result).toHaveLength(0)
    })

    it('should handle single item', () => {
      const data = [1]
      const totalPages = calculateTotalPages(1, 10)

      expect(totalPages).toBe(1)

      const result = paginateData(data, 1, 10)
      expect(result).toHaveLength(1)
      expect(result).toEqual([1])
    })

    it('should handle page size larger than dataset', () => {
      const data = Array.from({ length: 5 }, (_, i) => i)
      const totalPages = calculateTotalPages(5, 100)

      expect(totalPages).toBe(1)

      const result = paginateData(data, 1, 100)
      expect(result).toHaveLength(5)
      expect(result).toEqual(data)
    })

    it('should handle page size equal to dataset size', () => {
      const data = Array.from({ length: 10 }, (_, i) => i)
      const totalPages = calculateTotalPages(10, 10)

      expect(totalPages).toBe(1)

      const result = paginateData(data, 1, 10)
      expect(result).toHaveLength(10)
      expect(result).toEqual(data)
    })

    it('should handle very large dataset', () => {
      const total = 1000000
      const pageSize = 1000
      const totalPages = calculateTotalPages(total, pageSize)

      expect(totalPages).toBe(1000)

      const itemCount = calculatePageItemCount(1, pageSize, total)
      expect(itemCount).toBe(pageSize)

      const lastPageItemCount = calculatePageItemCount(totalPages, pageSize, total)
      expect(lastPageItemCount).toBe(pageSize)
    })

    it('should handle page size of 1', () => {
      const data = Array.from({ length: 10 }, (_, i) => i)
      const totalPages = calculateTotalPages(10, 1)

      expect(totalPages).toBe(10)

      for (let page = 1; page <= totalPages; page++) {
        const result = paginateData(data, page, 1)
        expect(result).toHaveLength(1)
        expect(result[0]).toBe(page - 1)
      }
    })
  })

  /**
   * 属性 4.7：分页数学属性
   *
   * 对于任何有效的分页参数，
   * 以下数学关系应该成立：
   * - totalPages = ceil(total / pageSize)
   * - 对于任何页码 page（1 <= page < totalPages），pageItemCount = pageSize
   * - 对于最后一页，pageItemCount = total - (totalPages - 1) * pageSize
   */
  describe('Property 4.7: Pagination Mathematical Properties', () => {
    it('should satisfy mathematical relationships', () => {
      const testCases = [
        { total: 100, pageSize: 10 },
        { total: 100, pageSize: 7 },
        { total: 35, pageSize: 10 },
        { total: 1, pageSize: 1 },
        { total: 1000, pageSize: 333 },
      ]

      testCases.forEach(({ total, pageSize }) => {
        const totalPages = calculateTotalPages(total, pageSize)

        // 验证 totalPages = ceil(total / pageSize)
        expect(totalPages).toBe(Math.ceil(total / pageSize))

        // 验证中间页的项目数 = pageSize
        if (totalPages > 1) {
          for (let page = 1; page < totalPages; page++) {
            const itemCount = calculatePageItemCount(page, pageSize, total)
            expect(itemCount).toBe(pageSize)
          }
        }

        // 验证最后一页的项目数
        if (totalPages > 0) {
          const lastPageItemCount = calculatePageItemCount(totalPages, pageSize, total)
          const expectedLastPageCount = total - (totalPages - 1) * pageSize
          expect(lastPageItemCount).toBe(expectedLastPageCount)
        }
      })
    })

    it('should satisfy sum property', () => {
      const testCases = [
        { total: 100, pageSize: 10 },
        { total: 100, pageSize: 7 },
        { total: 35, pageSize: 10 },
      ]

      testCases.forEach(({ total, pageSize }) => {
        const totalPages = calculateTotalPages(total, pageSize)

        let sum = 0
        for (let page = 1; page <= totalPages; page++) {
          const itemCount = calculatePageItemCount(page, pageSize, total)
          sum += itemCount
        }

        expect(sum).toBe(total)
      })
    })
  })

  /**
   * 属性 4.8：分页与数据类型无关
   *
   * 分页逻辑应该对任何数据类型都有效。
   */
  describe('Property 4.8: Pagination Type Independence', () => {
    it('should work with different data types', () => {
      // 数字数组
      const numbers = Array.from({ length: 20 }, (_, i) => i)
      const numbersPage = paginateData(numbers, 1, 5)
      expect(numbersPage).toHaveLength(5)

      // 字符串数组
      const strings = Array.from({ length: 20 }, (_, i) => `item-${i}`)
      const stringsPage = paginateData(strings, 1, 5)
      expect(stringsPage).toHaveLength(5)

      // 对象数组
      const objects = Array.from({ length: 20 }, (_, i) => ({
        id: i,
        name: `Item ${i}`,
      }))
      const objectsPage = paginateData(objects, 1, 5)
      expect(objectsPage).toHaveLength(5)

      // 结果项数组
      const results: ResultItem[] = Array.from({ length: 20 }, (_, i) => ({
        id: `result-${i}`,
        taskId: 'task-1',
        data: { value: i },
        sourceUrl: `https://example.com/${i}`,
        extractedAt: new Date().toISOString(),
      }))
      const resultsPage = paginateData(results, 1, 5)
      expect(resultsPage).toHaveLength(5)
    })
  })

  /**
   * 属性 4.9：分页稳定性
   *
   * 对于相同的输入，分页应该总是产生相同的输出。
   */
  describe('Property 4.9: Pagination Stability', () => {
    it('should produce consistent results for same input', () => {
      const data = Array.from({ length: 100 }, (_, i) => i)

      const result1 = paginateData(data, 5, 10)
      const result2 = paginateData(data, 5, 10)
      const result3 = paginateData(data, 5, 10)

      expect(result1).toEqual(result2)
      expect(result2).toEqual(result3)
    })

    it('should produce consistent total pages calculation', () => {
      const total1 = calculateTotalPages(100, 7)
      const total2 = calculateTotalPages(100, 7)
      const total3 = calculateTotalPages(100, 7)

      expect(total1).toBe(total2)
      expect(total2).toBe(total3)
    })

    it('should produce consistent item count calculation', () => {
      const count1 = calculatePageItemCount(5, 10, 100)
      const count2 = calculatePageItemCount(5, 10, 100)
      const count3 = calculatePageItemCount(5, 10, 100)

      expect(count1).toBe(count2)
      expect(count2).toBe(count3)
    })
  })
})
