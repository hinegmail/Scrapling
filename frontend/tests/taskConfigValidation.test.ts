import { describe, it, expect } from 'vitest'
import { validateTaskConfig, TaskConfig, ValidationResult } from '../src/api/tasks'

/**
 * 属性 2：任务配置验证
 * 
 * **Validates: Requirements 2.5**
 * 
 * 对于任何具有各种必填和可选字段组合的任务配置，验证系统应该正确识别缺失的必填字段并拒绝无效配置。
 */
describe('Property 2: Task Configuration Validation', () => {
  /**
   * 属性 2.1：必填字段验证
   * 
   * 对于任何缺少必填字段（name、targetUrl、fetcherType、selector、selectorType）的任务配置，
   * 验证器应该返回 isValid=false 并包含相应的错误消息。
   */
  describe('Property 2.1: Required Fields Validation', () => {
    it('should reject config with missing name', () => {
      const config: Partial<TaskConfig> = {
        targetUrl: 'https://example.com',
        fetcherType: 'http',
        selector: 'div.content',
        selectorType: 'css',
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'name',
          message: expect.stringContaining('必填'),
        })
      )
    })

    it('should reject config with empty name', () => {
      const config: Partial<TaskConfig> = {
        name: '   ',
        targetUrl: 'https://example.com',
        fetcherType: 'http',
        selector: 'div.content',
        selectorType: 'css',
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'name',
        })
      )
    })

    it('should reject config with missing targetUrl', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        fetcherType: 'http',
        selector: 'div.content',
        selectorType: 'css',
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'targetUrl',
        })
      )
    })

    it('should reject config with invalid URL format', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        targetUrl: 'not a valid url',
        fetcherType: 'http',
        selector: 'div.content',
        selectorType: 'css',
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'targetUrl',
          message: expect.stringContaining('格式无效'),
        })
      )
    })

    it('should reject config with missing fetcherType', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        targetUrl: 'https://example.com',
        selector: 'div.content',
        selectorType: 'css',
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'fetcherType',
        })
      )
    })

    it('should reject config with invalid fetcherType', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        targetUrl: 'https://example.com',
        fetcherType: 'invalid' as any,
        selector: 'div.content',
        selectorType: 'css',
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'fetcherType',
          message: expect.stringContaining('无效'),
        })
      )
    })

    it('should reject config with missing selector', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        targetUrl: 'https://example.com',
        fetcherType: 'http',
        selectorType: 'css',
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'selector',
        })
      )
    })

    it('should reject config with missing selectorType', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        targetUrl: 'https://example.com',
        fetcherType: 'http',
        selector: 'div.content',
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'selectorType',
        })
      )
    })

    it('should reject config with invalid selectorType', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        targetUrl: 'https://example.com',
        fetcherType: 'http',
        selector: 'div.content',
        selectorType: 'invalid' as any,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'selectorType',
          message: expect.stringContaining('无效'),
        })
      )
    })
  })

  /**
   * 属性 2.2：可选字段验证
   * 
   * 对于任何具有无效可选字段值的任务配置（timeout、retryCount、waitTime、viewportWidth、viewportHeight），
   * 验证器应该返回 isValid=false 并包含相应的错误消息。
   */
  describe('Property 2.2: Optional Fields Validation', () => {
    const validBaseConfig: Partial<TaskConfig> = {
      name: 'Test Task',
      targetUrl: 'https://example.com',
      fetcherType: 'http',
      selector: 'div.content',
      selectorType: 'css',
    }

    it('should reject config with negative timeout', () => {
      const config: Partial<TaskConfig> = {
        ...validBaseConfig,
        timeout: -1,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'timeout',
          message: expect.stringContaining('正整数'),
        })
      )
    })

    it('should reject config with zero timeout', () => {
      const config: Partial<TaskConfig> = {
        ...validBaseConfig,
        timeout: 0,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'timeout',
        })
      )
    })

    it('should reject config with non-integer timeout', () => {
      const config: Partial<TaskConfig> = {
        ...validBaseConfig,
        timeout: 3.14,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'timeout',
        })
      )
    })

    it('should reject config with negative retryCount', () => {
      const config: Partial<TaskConfig> = {
        ...validBaseConfig,
        retryCount: -1,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'retryCount',
          message: expect.stringContaining('非负整数'),
        })
      )
    })

    it('should reject config with non-integer retryCount', () => {
      const config: Partial<TaskConfig> = {
        ...validBaseConfig,
        retryCount: 2.5,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'retryCount',
        })
      )
    })

    it('should reject config with negative waitTime', () => {
      const config: Partial<TaskConfig> = {
        ...validBaseConfig,
        waitTime: -1,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'waitTime',
        })
      )
    })

    it('should reject config with negative viewportWidth', () => {
      const config: Partial<TaskConfig> = {
        ...validBaseConfig,
        viewportWidth: -1,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'viewportWidth',
        })
      )
    })

    it('should reject config with zero viewportHeight', () => {
      const config: Partial<TaskConfig> = {
        ...validBaseConfig,
        viewportHeight: 0,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'viewportHeight',
        })
      )
    })
  })

  /**
   * 属性 2.3：有效配置接受
   * 
   * 对于任何具有所有必填字段且所有可选字段有效的任务配置，
   * 验证器应该返回 isValid=true 且 errors 数组为空。
   */
  describe('Property 2.3: Valid Configuration Acceptance', () => {
    it('should accept config with all required fields', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        targetUrl: 'https://example.com',
        fetcherType: 'http',
        selector: 'div.content',
        selectorType: 'css',
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should accept config with valid optional fields', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        targetUrl: 'https://example.com',
        fetcherType: 'dynamic',
        selector: '//div[@class="content"]',
        selectorType: 'xpath',
        timeout: 30,
        retryCount: 3,
        waitTime: 5,
        viewportWidth: 1920,
        viewportHeight: 1080,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should accept config with zero retryCount', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        targetUrl: 'https://example.com',
        fetcherType: 'http',
        selector: 'div.content',
        selectorType: 'css',
        retryCount: 0,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should accept config with zero waitTime', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        targetUrl: 'https://example.com',
        fetcherType: 'dynamic',
        selector: 'div.content',
        selectorType: 'css',
        waitTime: 0,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should accept config with all fetcher types', () => {
      const fetcherTypes: Array<'http' | 'dynamic' | 'stealthy'> = ['http', 'dynamic', 'stealthy']

      fetcherTypes.forEach((fetcherType) => {
        const config: Partial<TaskConfig> = {
          name: 'Test Task',
          targetUrl: 'https://example.com',
          fetcherType,
          selector: 'div.content',
          selectorType: 'css',
        }

        const result = validateTaskConfig(config)

        expect(result.isValid).toBe(true)
        expect(result.errors).toHaveLength(0)
      })
    })

    it('should accept config with all selector types', () => {
      const selectorTypes: Array<'css' | 'xpath'> = ['css', 'xpath']

      selectorTypes.forEach((selectorType) => {
        const config: Partial<TaskConfig> = {
          name: 'Test Task',
          targetUrl: 'https://example.com',
          fetcherType: 'http',
          selector: selectorType === 'css' ? 'div.content' : '//div[@class="content"]',
          selectorType,
        }

        const result = validateTaskConfig(config)

        expect(result.isValid).toBe(true)
        expect(result.errors).toHaveLength(0)
      })
    })
  })

  /**
   * 属性 2.4：多个错误检测
   * 
   * 对于任何具有多个无效字段的任务配置，
   * 验证器应该返回 isValid=false 并包含所有无效字段的错误消息。
   */
  describe('Property 2.4: Multiple Errors Detection', () => {
    it('should detect multiple missing required fields', () => {
      const config: Partial<TaskConfig> = {
        name: '',
        targetUrl: '',
        fetcherType: undefined,
        selector: '',
        selectorType: undefined,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(1)
      expect(result.errors.map((e) => e.field)).toContain('name')
      expect(result.errors.map((e) => e.field)).toContain('targetUrl')
      expect(result.errors.map((e) => e.field)).toContain('fetcherType')
      expect(result.errors.map((e) => e.field)).toContain('selector')
      expect(result.errors.map((e) => e.field)).toContain('selectorType')
    })

    it('should detect multiple invalid optional fields', () => {
      const config: Partial<TaskConfig> = {
        name: 'Test Task',
        targetUrl: 'https://example.com',
        fetcherType: 'http',
        selector: 'div.content',
        selectorType: 'css',
        timeout: -1,
        retryCount: -1,
        viewportWidth: 0,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThanOrEqual(3)
      expect(result.errors.map((e) => e.field)).toContain('timeout')
      expect(result.errors.map((e) => e.field)).toContain('retryCount')
      expect(result.errors.map((e) => e.field)).toContain('viewportWidth')
    })

    it('should detect both required and optional field errors', () => {
      const config: Partial<TaskConfig> = {
        name: '',
        targetUrl: 'invalid-url',
        fetcherType: 'invalid' as any,
        selector: 'div.content',
        selectorType: 'css',
        timeout: -1,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThanOrEqual(4)
    })
  })

  /**
   * 属性 2.5：错误消息一致性
   * 
   * 对于任何无效的任务配置，
   * 验证器返回的每个错误都应该包含 field 和 message 属性，且 message 不为空。
   */
  describe('Property 2.5: Error Message Consistency', () => {
    it('should have consistent error structure', () => {
      const config: Partial<TaskConfig> = {
        name: '',
        targetUrl: 'invalid',
        fetcherType: 'invalid' as any,
      }

      const result = validateTaskConfig(config)

      expect(result.isValid).toBe(false)
      result.errors.forEach((error) => {
        expect(error).toHaveProperty('field')
        expect(error).toHaveProperty('message')
        expect(typeof error.field).toBe('string')
        expect(typeof error.message).toBe('string')
        expect(error.field.length).toBeGreaterThan(0)
        expect(error.message.length).toBeGreaterThan(0)
      })
    })

    it('should have unique error fields', () => {
      const config: Partial<TaskConfig> = {
        name: '',
        targetUrl: 'invalid',
        fetcherType: 'invalid' as any,
        selector: '',
        selectorType: 'invalid' as any,
        timeout: -1,
      }

      const result = validateTaskConfig(config)

      const fields = result.errors.map((e) => e.field)
      const uniqueFields = new Set(fields)
      expect(uniqueFields.size).toBe(fields.length)
    })
  })

  /**
   * 属性 2.6：URL 验证准确性
   * 
   * 对于任何 URL 字符串，验证器应该正确识别有效的 URL（http/https 协议）
   * 和无效的 URL（格式错误、缺少协议等）。
   */
  describe('Property 2.6: URL Validation Accuracy', () => {
    const validUrls = [
      'https://example.com',
      'http://example.com',
      'https://example.com/path',
      'https://example.com:8080',
      'https://example.com/path?query=value',
      'https://example.com/path#fragment',
      'https://subdomain.example.com',
      'https://example.co.uk',
    ]

    validUrls.forEach((url) => {
      it(`should accept valid URL: ${url}`, () => {
        const config: Partial<TaskConfig> = {
          name: 'Test Task',
          targetUrl: url,
          fetcherType: 'http',
          selector: 'div',
          selectorType: 'css',
        }

        const result = validateTaskConfig(config)

        expect(result.isValid).toBe(true)
        expect(result.errors.filter((e) => e.field === 'targetUrl')).toHaveLength(0)
      })
    })

    const invalidUrls = [
      'not a url',
      'example.com',
      'ftp://example.com',
      'htp://example.com',
      '://example.com',
      'https://',
      'https://.',
      '',
    ]

    invalidUrls.forEach((url) => {
      it(`should reject invalid URL: ${url}`, () => {
        const config: Partial<TaskConfig> = {
          name: 'Test Task',
          targetUrl: url,
          fetcherType: 'http',
          selector: 'div',
          selectorType: 'css',
        }

        const result = validateTaskConfig(config)

        if (url === '') {
          expect(result.errors.some((e) => e.field === 'targetUrl')).toBe(true)
        } else {
          expect(result.errors.some((e) => e.field === 'targetUrl')).toBe(true)
        }
      })
    })
  })

  /**
   * 属性 2.7：数值范围验证
   * 
   * 对于任何数值字段（timeout、retryCount、waitTime、viewportWidth、viewportHeight），
   * 验证器应该正确检查值是否在允许的范围内。
   */
  describe('Property 2.7: Numeric Range Validation', () => {
    const validBaseConfig: Partial<TaskConfig> = {
      name: 'Test Task',
      targetUrl: 'https://example.com',
      fetcherType: 'http',
      selector: 'div.content',
      selectorType: 'css',
    }

    it('should accept positive timeout values', () => {
      const timeouts = [1, 10, 30, 60, 300, 3600]

      timeouts.forEach((timeout) => {
        const config: Partial<TaskConfig> = {
          ...validBaseConfig,
          timeout,
        }

        const result = validateTaskConfig(config)

        expect(result.errors.filter((e) => e.field === 'timeout')).toHaveLength(0)
      })
    })

    it('should accept non-negative retryCount values', () => {
      const retryCounts = [0, 1, 5, 10, 100]

      retryCounts.forEach((retryCount) => {
        const config: Partial<TaskConfig> = {
          ...validBaseConfig,
          retryCount,
        }

        const result = validateTaskConfig(config)

        expect(result.errors.filter((e) => e.field === 'retryCount')).toHaveLength(0)
      })
    })

    it('should accept non-negative waitTime values', () => {
      const waitTimes = [0, 1, 5, 10, 60]

      waitTimes.forEach((waitTime) => {
        const config: Partial<TaskConfig> = {
          ...validBaseConfig,
          waitTime,
        }

        const result = validateTaskConfig(config)

        expect(result.errors.filter((e) => e.field === 'waitTime')).toHaveLength(0)
      })
    })

    it('should accept positive viewport dimensions', () => {
      const dimensions = [640, 800, 1024, 1280, 1920, 2560]

      dimensions.forEach((dimension) => {
        const config: Partial<TaskConfig> = {
          ...validBaseConfig,
          viewportWidth: dimension,
          viewportHeight: dimension,
        }

        const result = validateTaskConfig(config)

        expect(result.errors.filter((e) => e.field === 'viewportWidth')).toHaveLength(0)
        expect(result.errors.filter((e) => e.field === 'viewportHeight')).toHaveLength(0)
      })
    })
  })

  /**
   * 属性 2.8：字符串修剪
   * 
   * 对于任何包含仅空格的字符串字段（name、selector），
   * 验证器应该将其视为缺失的必填字段。
   */
  describe('Property 2.8: String Trimming', () => {
    it('should treat whitespace-only name as missing', () => {
      const whitespaces = ['', ' ', '  ', '\t', '\n', '\r\n']

      whitespaces.forEach((ws) => {
        const config: Partial<TaskConfig> = {
          name: ws,
          targetUrl: 'https://example.com',
          fetcherType: 'http',
          selector: 'div',
          selectorType: 'css',
        }

        const result = validateTaskConfig(config)

        expect(result.errors.some((e) => e.field === 'name')).toBe(true)
      })
    })

    it('should treat whitespace-only selector as missing', () => {
      const whitespaces = ['', ' ', '  ', '\t', '\n']

      whitespaces.forEach((ws) => {
        const config: Partial<TaskConfig> = {
          name: 'Test Task',
          targetUrl: 'https://example.com',
          fetcherType: 'http',
          selector: ws,
          selectorType: 'css',
        }

        const result = validateTaskConfig(config)

        expect(result.errors.some((e) => e.field === 'selector')).toBe(true)
      })
    })

    it('should treat whitespace-only targetUrl as missing', () => {
      const whitespaces = ['', ' ', '  ', '\t']

      whitespaces.forEach((ws) => {
        const config: Partial<TaskConfig> = {
          name: 'Test Task',
          targetUrl: ws,
          fetcherType: 'http',
          selector: 'div',
          selectorType: 'css',
        }

        const result = validateTaskConfig(config)

        expect(result.errors.some((e) => e.field === 'targetUrl')).toBe(true)
      })
    })
  })
})
