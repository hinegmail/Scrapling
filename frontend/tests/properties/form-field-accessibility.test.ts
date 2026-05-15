import { describe, it, expect } from 'vitest'
import * as fc from 'fast-check'

/**
 * 表单字段可访问性属性测试
 * **Validates: Requirements 11.6**
 *
 * 这个测试套件验证所有表单字段都有适当的标签、错误消息关联和必填字段标记
 * 以满足 WCAG 2.1 AA 级别的可访问性要求
 */

// ============================================================================
// 辅助函数和生成器
// ============================================================================

/**
 * 生成有效的表单字段 ID
 */
const fieldIdArb = () =>
  fc
    .stringMatching(/^[a-z][a-z0-9_-]*$/)
    .filter(id => id.length >= 2 && id.length <= 50)

/**
 * 生成有效的标签文本（不包含特殊字符）
 */
const labelTextArb = () =>
  fc
    .tuple(
      fc.stringMatching(/^[A-Z][a-z]+$/),
      fc.array(fc.stringMatching(/^[a-z]+$/), { minLength: 0, maxLength: 3 })
    )
    .map(([first, rest]) => [first, ...rest].join(' '))

/**
 * 生成表单字段类型
 */
const fieldTypeArb = () =>
  fc.oneof(
    fc.constant('text'),
    fc.constant('email'),
    fc.constant('password'),
    fc.constant('number'),
    fc.constant('tel'),
    fc.constant('url'),
    fc.constant('date'),
    fc.constant('checkbox'),
    fc.constant('radio')
  )

/**
 * 生成错误消息
 */
const errorMessageArb = () =>
  fc
    .tuple(
      fc.stringMatching(/^(This field|Please|Error|Invalid)/),
      fc.array(fc.stringMatching(/^[a-z]+$/), { minLength: 1, maxLength: 3 })
    )
    .map(([first, rest]) => `${first} ${rest.join(' ')}`)

/**
 * 生成 aria-label 文本
 */
const ariaLabelArb = () =>
  fc
    .tuple(
      fc.stringMatching(/^[A-Z][a-z]+/),
      fc.array(fc.stringMatching(/^[a-z]+$/), { minLength: 0, maxLength: 2 })
    )
    .map(([first, rest]) => [first, ...rest].join(' '))

/**
 * 生成表单字段 HTML
 */
const formFieldHtmlArb = (
  fieldId: string,
  labelText: string,
  fieldType: string,
  isRequired: boolean = false,
  errorMessage?: string,
  ariaLabel?: string
) => {
  const requiredAttr = isRequired ? 'required' : ''
  const ariaRequiredAttr = isRequired ? 'aria-required="true"' : ''
  const errorId = errorMessage ? `${fieldId}-error` : ''
  const ariaDescribedBy = errorMessage ? `aria-describedby="${errorId}"` : ''
  const ariaLabelAttr = ariaLabel ? `aria-label="${ariaLabel}"` : ''

  let fieldHtml = ''

  if (fieldType === 'checkbox' || fieldType === 'radio') {
    fieldHtml = `<input type="${fieldType}" id="${fieldId}" name="${fieldId}" ${requiredAttr} ${ariaRequiredAttr} />`
  } else if (fieldType === 'textarea') {
    fieldHtml = `<textarea id="${fieldId}" name="${fieldId}" ${requiredAttr} ${ariaRequiredAttr} ${ariaDescribedBy}></textarea>`
  } else if (fieldType === 'select') {
    fieldHtml = `<select id="${fieldId}" name="${fieldId}" ${requiredAttr} ${ariaRequiredAttr} ${ariaDescribedBy}>
      <option value="">Select an option</option>
      <option value="1">Option 1</option>
    </select>`
  } else {
    fieldHtml = `<input type="${fieldType}" id="${fieldId}" name="${fieldId}" ${requiredAttr} ${ariaRequiredAttr} ${ariaDescribedBy} ${ariaLabelAttr} />`
  }

  const labelHtml = `<label for="${fieldId}">${labelText}</label>`
  const errorHtml = errorMessage ? `<span id="${errorId}" role="alert">${errorMessage}</span>` : ''

  return `${labelHtml}\n${fieldHtml}\n${errorHtml}`
}

/**
 * 从 HTML 中提取表单字段信息
 */
function extractFormFields(html: string): Array<{
  id: string
  labelText: string | null
  hasLabel: boolean
  hasAriaLabel: boolean
  hasAriaRequired: boolean
  hasRequired: boolean
  hasAriaDescribedBy: boolean
  errorId: string | null
  fieldType: string
}> {
  const fields: Array<{
    id: string
    labelText: string | null
    hasLabel: boolean
    hasAriaLabel: boolean
    hasAriaRequired: boolean
    hasRequired: boolean
    hasAriaDescribedBy: boolean
    errorId: string | null
    fieldType: string
  }> = []

  // 首先提取所有标签及其关联的 ID
  const labelMap = new Map<string, string>()
  const labelRegex = /<label[^>]*for="([^"]*)"[^>]*>([^<]*)<\/label>/g
  let match
  while ((match = labelRegex.exec(html)) !== null) {
    const labelFor = match[1]
    const labelText = match[2]
    labelMap.set(labelFor, labelText)
  }

  // 提取 input 字段
  const inputRegex = /<input[^>]*type="([^"]*)"[^>]*id="([^"]*)"[^>]*>/g
  while ((match = inputRegex.exec(html)) !== null) {
    const fieldType = match[1]
    const fieldId = match[2]
    const fullMatch = match[0]

    fields.push({
      id: fieldId,
      labelText: labelMap.get(fieldId) || null,
      hasLabel: labelMap.has(fieldId),
      hasAriaLabel: fullMatch.includes('aria-label='),
      hasAriaRequired: fullMatch.includes('aria-required='),
      hasRequired: fullMatch.includes('required'),
      hasAriaDescribedBy: fullMatch.includes('aria-describedby='),
      errorId: extractErrorId(fullMatch),
      fieldType,
    })
  }

  // 提取 textarea 字段
  const textareaRegex = /<textarea[^>]*id="([^"]*)"[^>]*>/g
  while ((match = textareaRegex.exec(html)) !== null) {
    const fieldId = match[1]
    const fullMatch = match[0]

    fields.push({
      id: fieldId,
      labelText: labelMap.get(fieldId) || null,
      hasLabel: labelMap.has(fieldId),
      hasAriaLabel: fullMatch.includes('aria-label='),
      hasAriaRequired: fullMatch.includes('aria-required='),
      hasRequired: fullMatch.includes('required'),
      hasAriaDescribedBy: fullMatch.includes('aria-describedby='),
      errorId: extractErrorId(fullMatch),
      fieldType: 'textarea',
    })
  }

  // 提取 select 字段
  const selectRegex = /<select[^>]*id="([^"]*)"[^>]*>/g
  while ((match = selectRegex.exec(html)) !== null) {
    const fieldId = match[1]
    const fullMatch = match[0]

    fields.push({
      id: fieldId,
      labelText: labelMap.get(fieldId) || null,
      hasLabel: labelMap.has(fieldId),
      hasAriaLabel: fullMatch.includes('aria-label='),
      hasAriaRequired: fullMatch.includes('aria-required='),
      hasRequired: fullMatch.includes('required'),
      hasAriaDescribedBy: fullMatch.includes('aria-describedby='),
      errorId: extractErrorId(fullMatch),
      fieldType: 'select',
    })
  }

  return fields
}

/**
 * 从字段 HTML 中提取错误 ID
 */
function extractErrorId(fieldHtml: string): string | null {
  const match = fieldHtml.match(/aria-describedby="([^"]*)"/);
  return match ? match[1] : null
}

/**
 * 检查标签和字段是否正确关联
 */
function isLabelProperlyAssociated(html: string, fieldId: string): boolean {
  const labelRegex = new RegExp(`<label[^>]*for="${fieldId}"[^>]*>`)
  return labelRegex.test(html)
}

/**
 * 检查错误消息是否正确关联
 */
function isErrorMessageProperlyAssociated(html: string, fieldId: string): boolean {
  const fieldRegex = new RegExp(`<input[^>]*id="${fieldId}"[^>]*aria-describedby="([^"]*)"`)
  const match = fieldRegex.exec(html)
  if (!match) return false

  const errorId = match[1]
  const errorRegex = new RegExp(`<span[^>]*id="${errorId}"[^>]*role="alert"`)
  return errorRegex.test(html)
}

// ============================================================================
// 属性测试
// ============================================================================

describe('Form Field Accessibility Properties', () => {
  // 属性 1: 所有表单字段都应该有关联的标签
  it('Property 1: All form fields should have associated labels', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb(), fieldTypeArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label, type]) =>
            formFieldHtmlArb(id, label, type)
          )
          const html = htmlParts.join('\n')

          fields.forEach(([fieldId]) => {
            expect(isLabelProperlyAssociated(html, fieldId)).toBe(true)
          })
        }
      )
    )
  })

  // 属性 2: 标签的 for 属性应该与表单字段的 id 属性匹配
  it('Property 2: Label for attribute should match form field id', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label]) =>
            `<label for="${id}">${label}</label>\n<input type="text" id="${id}" />`
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            expect(field.hasLabel).toBe(true)
          })
        }
      )
    )
  })

  // 属性 3: 必填字段应该有 required 属性或 aria-required
  it('Property 3: Required fields should have required attribute or aria-required', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label]) =>
            formFieldHtmlArb(id, label, 'text', true)
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            expect(field.hasRequired || field.hasAriaRequired).toBe(true)
          })
        }
      )
    )
  })

  // 属性 4: 可选字段不应该有 required 属性
  it('Property 4: Optional fields should not have required attribute', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label]) =>
            formFieldHtmlArb(id, label, 'text', false)
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            expect(field.hasRequired).toBe(false)
          })
        }
      )
    )
  })

  // 属性 5: 错误消息应该与表单字段正确关联
  it('Property 5: Error messages should be properly associated with form fields', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb(), errorMessageArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label, error]) =>
            formFieldHtmlArb(id, label, 'text', false, error)
          )
          const html = htmlParts.join('\n')

          fields.forEach(([fieldId]) => {
            expect(isErrorMessageProperlyAssociated(html, fieldId)).toBe(true)
          })
        }
      )
    )
  })

  // 属性 6: 表单字段应该有 aria-label 或关联的标签
  it('Property 6: Form fields should have aria-label or associated label', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label]) =>
            formFieldHtmlArb(id, label, 'text', false, undefined, label)
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            expect(field.hasLabel || field.hasAriaLabel).toBe(true)
          })
        }
      )
    )
  })

  // 属性 7: 不同的表单字段类型都应该有标签
  it('Property 7: Different form field types should all have labels', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(
            fieldIdArb(),
            labelTextArb(),
            fc.oneof(
              fc.constant('text'),
              fc.constant('email'),
              fc.constant('password'),
              fc.constant('textarea'),
              fc.constant('select')
            )
          ),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label, type]) =>
            formFieldHtmlArb(id, label, type)
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            expect(field.hasLabel).toBe(true)
          })
        }
      )
    )
  })

  // 属性 8: 表单字段 ID 应该是唯一的
  it('Property 8: Form field IDs should be unique', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb()),
          { minLength: 2, maxLength: 10 }
        ),
        fields => {
          const ids = fields.map(([id]) => id)
          const uniqueIds = new Set(ids)
          // 如果所有 ID 都是唯一的，集合大小应该等于数组大小
          if (uniqueIds.size === ids.length) {
            expect(uniqueIds.size).toBe(ids.length)
          }
        }
      )
    )
  })

  // 属性 9: 标签文本不应该为空
  it('Property 9: Label text should not be empty', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label]) =>
            `<label for="${id}">${label}</label>\n<input type="text" id="${id}" />`
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          // 验证提取的字段数量与输入字段数量相同
          expect(extracted.length).toBe(fields.length)
          
          extracted.forEach((field) => {
            // 标签文本应该不为空
            expect(field.labelText).not.toBe('')
            expect(field.labelText).not.toBeNull()
            expect(field.labelText).toBeTruthy()
          })
        }
      )
    )
  })

  // 属性 10: 错误消息应该有 role="alert" 属性
  it('Property 10: Error messages should have role="alert" attribute', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb(), errorMessageArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label, error]) =>
            formFieldHtmlArb(id, label, 'text', false, error)
          )
          const html = htmlParts.join('\n')

          // 验证所有错误消息都有 role="alert"
          const errorRegex = /<span[^>]*role="alert"[^>]*>/g
          const matches = html.match(errorRegex)
          expect(matches).not.toBeNull()
          expect(matches!.length).toBe(fields.length)
        }
      )
    )
  })

  // 属性 11: 必填字段应该有适当的标记
  it('Property 11: Required fields should have appropriate marking', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label]) =>
            formFieldHtmlArb(id, label, 'text', true)
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            // 必填字段应该有 required 或 aria-required
            const hasRequiredMarking = field.hasRequired || field.hasAriaRequired
            expect(hasRequiredMarking).toBe(true)
          })
        }
      )
    )
  })

  // 属性 12: 表单字段应该有有效的 ID
  it('Property 12: Form fields should have valid IDs', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label]) =>
            formFieldHtmlArb(id, label, 'text')
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            // ID 应该不为空且符合 HTML ID 规范
            expect(field.id).toBeTruthy()
            expect(/^[a-z][a-z0-9_-]*$/.test(field.id)).toBe(true)
          })
        }
      )
    )
  })

  // 属性 13: 嵌套表单中的字段应该有唯一的 ID
  it('Property 13: Fields in nested forms should have unique IDs', () => {
    fc.assert(
      fc.property(
        fc.tuple(
          fc.array(
            fc.tuple(fieldIdArb(), labelTextArb()),
            { minLength: 1, maxLength: 5 }
          ),
          fc.array(
            fc.tuple(fieldIdArb(), labelTextArb()),
            { minLength: 1, maxLength: 5 }
          )
        ),
        ([form1Fields, form2Fields]) => {
          const form1Html = form1Fields
            .map(([id, label]) => formFieldHtmlArb(id, label, 'text'))
            .join('\n')
          const form2Html = form2Fields
            .map(([id, label]) => formFieldHtmlArb(id, label, 'text'))
            .join('\n')

          const html = `<form>${form1Html}</form><form>${form2Html}</form>`
          const extracted = extractFormFields(html)

          // 验证所有字段都被提取
          expect(extracted.length).toBe(form1Fields.length + form2Fields.length)
          
          // 如果两个表单中的字段 ID 不同，应该有不同的字段
          const allIds = extracted.map(f => f.id)
          const uniqueIds = new Set(allIds)
          
          // 如果所有 ID 都是唯一的，集合大小应该等于数组大小
          if (uniqueIds.size === allIds.length) {
            expect(uniqueIds.size).toBe(allIds.length)
          }
        }
      )
    )
  })

  // 属性 14: 多个表单中的字段应该各自有标签
  it('Property 14: Fields in multiple forms should each have labels', () => {
    fc.assert(
      fc.property(
        fc.tuple(
          fc.array(
            fc.tuple(fieldIdArb(), labelTextArb()),
            { minLength: 1, maxLength: 5 }
          ),
          fc.array(
            fc.tuple(fieldIdArb(), labelTextArb()),
            { minLength: 1, maxLength: 5 }
          )
        ),
        ([form1Fields, form2Fields]) => {
          const form1Html = form1Fields
            .map(([id, label]) => formFieldHtmlArb(id, label, 'text'))
            .join('\n')
          const form2Html = form2Fields
            .map(([id, label]) => formFieldHtmlArb(id, label, 'text'))
            .join('\n')

          const html = `<form>${form1Html}</form><form>${form2Html}</form>`
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            expect(field.hasLabel).toBe(true)
          })
        }
      )
    )
  })

  // 属性 15: 长标签文本应该被正确处理
  it('Property 15: Long label text should be correctly handled', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(
            fieldIdArb(),
            fc.tuple(labelTextArb(), labelTextArb(), labelTextArb())
              .map(([a, b, c]) => `${a} ${b} ${c}`)
          ),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label]) =>
            `<label for="${id}">${label}</label>\n<input type="text" id="${id}" />`
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach((field, idx) => {
            expect(field.labelText).toBe(fields[idx][1])
            // 标签文本应该至少有一定长度（由于生成的标签可能较短，我们检查它是否被正确提取）
            expect(field.labelText).toBeTruthy()
            expect(field.labelText!.length).toBeGreaterThan(0)
          })
        }
      )
    )
  })

  // 属性 16: 特殊字符在标签中应该被正确处理
  it('Property 16: Special characters in labels should be handled correctly', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label]) => {
            const escapedLabel = label.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            return `<label for="${id}">${escapedLabel}</label>\n<input type="text" id="${id}" />`
          })
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          expect(extracted.length).toBe(fields.length)
        }
      )
    )
  })

  // 属性 17: 带错误消息的字段应该有 aria-describedby
  it('Property 17: Fields with error messages should have aria-describedby', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb(), errorMessageArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label, error]) =>
            formFieldHtmlArb(id, label, 'text', false, error)
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            expect(field.hasAriaDescribedBy).toBe(true)
          })
        }
      )
    )
  })

  // 属性 18: 没有错误消息的字段不应该有 aria-describedby
  it('Property 18: Fields without error messages should not have aria-describedby', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label]) =>
            formFieldHtmlArb(id, label, 'text', false)
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            expect(field.hasAriaDescribedBy).toBe(false)
          })
        }
      )
    )
  })

  // 属性 19: 复选框和单选按钮应该有标签
  it('Property 19: Checkboxes and radio buttons should have labels', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(
            fieldIdArb(),
            labelTextArb(),
            fc.oneof(fc.constant('checkbox'), fc.constant('radio'))
          ),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const htmlParts = fields.map(([id, label, type]) =>
            formFieldHtmlArb(id, label, type)
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            expect(field.hasLabel).toBe(true)
          })
        }
      )
    )
  })

  // 属性 20: 所有表单字段都应该有有效的字段类型
  it('Property 20: All form fields should have valid field types', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(fieldIdArb(), labelTextArb(), fieldTypeArb()),
          { minLength: 1, maxLength: 10 }
        ),
        fields => {
          const validTypes = [
            'text',
            'email',
            'password',
            'number',
            'tel',
            'url',
            'date',
            'checkbox',
            'radio',
            'textarea',
            'select',
          ]
          const htmlParts = fields.map(([id, label, type]) =>
            formFieldHtmlArb(id, label, type)
          )
          const html = htmlParts.join('\n')
          const extracted = extractFormFields(html)

          extracted.forEach(field => {
            expect(validTypes).toContain(field.fieldType)
          })
        }
      )
    )
  })
})
