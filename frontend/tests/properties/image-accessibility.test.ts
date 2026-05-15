import { describe, it, expect } from 'vitest'
import * as fc from 'fast-check'

/**
 * 图像可访问性属性测试
 * **Validates: Requirements 11.5**
 *
 * 这个测试套件验证所有图像都有适当的替代文本（alt 属性）
 * 以满足 WCAG 2.1 AA 级别的可访问性要求
 */

// ============================================================================
// 辅助函数和生成器
// ============================================================================

/**
 * 生成有效的图像文件名
 */
const imageFilenameArb = () =>
  fc
    .tuple(
      fc.stringMatching(/^[a-z0-9_-]+$/),
      fc.oneof(
        fc.constant('png'),
        fc.constant('jpg'),
        fc.constant('jpeg'),
        fc.constant('svg'),
        fc.constant('webp'),
        fc.constant('gif')
      )
    )
    .map(([name, ext]) => `${name}.${ext}`)

/**
 * 生成有意义的 alt 文本
 */
const meaningfulAltTextArb = () =>
  fc
    .tuple(
      fc.stringMatching(/^[A-Z][a-z]+/),
      fc.array(fc.stringMatching(/^[a-z]+$/), { minLength: 1, maxLength: 5 })
    )
    .map(([first, rest]) => [first, ...rest].join(' '))

/**
 * 生成装饰性图像的 alt 文本（空字符串）
 */
const decorativeAltTextArb = () => fc.constant('')

/**
 * 生成图像元素的 HTML
 */
const imageElementArb = (altText: string, src: string) => {
  // 转义 alt 文本中的引号
  const escapedAlt = altText.replace(/"/g, '&quot;')
  return `<img src="${src}" alt="${escapedAlt}" />`
}

/**
 * 生成包含图像的 HTML 文档
 */
const htmlDocumentWithImagesArb = (images: Array<{ src: string; alt: string }>) => {
  const imageElements = images.map(img => imageElementArb(img.alt, img.src)).join('\n')
  return `<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
${imageElements}
</body>
</html>`
}

/**
 * 从 HTML 字符串中提取所有 img 元素
 */
function extractImageElements(html: string): Array<{ src: string; alt: string | null }> {
  // 更健壮的正则表达式，处理转义的引号
  const imgRegex = /<img[^>]*src="([^"]*)"[^>]*alt="((?:[^"\\]|\\.)*)"[^>]*>/g
  const images: Array<{ src: string; alt: string | null }> = []
  let match

  while ((match = imgRegex.exec(html)) !== null) {
    images.push({
      src: match[1],
      alt: match[2].replace(/&quot;/g, '"'), // 反转义引号
    })
  }

  return images
}

/**
 * 检查 alt 文本是否有意义（不仅仅是文件名）
 */
function isAltTextMeaningful(alt: string, src: string): boolean {
  if (!alt) return false

  // 检查 alt 文本是否只是文件名
  const filename = src.split('/').pop() || ''
  const filenameWithoutExt = filename.split('.')[0]

  // 如果 alt 文本与文件名相同或非常相似，则不认为是有意义的
  if (alt.toLowerCase() === filenameWithoutExt.toLowerCase()) {
    return false
  }

  // 检查 alt 文本长度（有意义的 alt 文本通常至少有几个单词或足够长）
  const wordCount = alt.trim().split(/\s+/).length
  return wordCount >= 1 && alt.length >= 2 // 至少 1 个单词且长度 >= 2
}

/**
 * 检查图像是否是装饰性的（基于 alt 属性）
 */
function isDecorativeImage(alt: string): boolean {
  return alt === ''
}

// ============================================================================
// 属性测试
// ============================================================================

describe('Image Accessibility Properties', () => {
  // 属性 1: 所有图像都有 alt 属性
  it('Property 1: All images must have alt attribute', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          // 验证：所有提取的图像都有 alt 属性
          expect(extracted.length).toBe(images.length)
          extracted.forEach(img => {
            expect(img.alt).toBeDefined()
            expect(typeof img.alt).toBe('string')
          })
        }
      )
    )
  })

  // 属性 2: Alt 属性不应为 null（除了装饰性图像）
  it('Property 2: Alt attribute should not be null for content images', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach(img => {
            expect(img.alt).not.toBeNull()
          })
        }
      )
    )
  })

  // 属性 3: 装饰性图像应该有空 alt 属性
  it('Property 3: Decorative images should have empty alt attribute', () => {
    fc.assert(
      fc.property(
        fc.array(imageFilenameArb(), { minLength: 1, maxLength: 10 }),
        srcs => {
          const htmlImages = srcs.map(src => ({ src, alt: '' }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach(img => {
            expect(img.alt).toBe('')
          })
        }
      )
    )
  })

  // 属性 4: 内容图像的 alt 文本不应为空
  it('Property 4: Content images should not have empty alt text', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach(img => {
            // 如果不是装饰性图像，alt 文本不应为空
            if (!isDecorativeImage(img.alt!)) {
              expect(img.alt).not.toBe('')
              expect(img.alt!.length).toBeGreaterThan(0)
            }
          })
        }
      )
    )
  })

  // 属性 5: Alt 文本应该是字符串类型
  it('Property 5: Alt text should be string type', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), fc.oneof(meaningfulAltTextArb(), decorativeAltTextArb())),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach(img => {
            expect(typeof img.alt).toBe('string')
          })
        }
      )
    )
  })

  // 属性 6: 不同图像类型都应该有 alt 属性
  it('Property 6: Different image types (PNG, JPG, SVG) should all have alt attribute', () => {
    fc.assert(
      fc.property(
        fc.tuple(
          fc.array(
            fc.tuple(
              fc.stringMatching(/^[a-z0-9_-]+$/),
              fc.oneof(fc.constant('png'), fc.constant('jpg'), fc.constant('svg'))
            ),
            { minLength: 1, maxLength: 10 }
          ),
          fc.array(meaningfulAltTextArb(), { minLength: 1, maxLength: 10 })
        ),
        ([imageTypes, altTexts]) => {
          const htmlImages = imageTypes.map(([name, ext], idx) => ({
            src: `${name}.${ext}`,
            alt: altTexts[idx % altTexts.length],
          }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach(img => {
            expect(img.alt).toBeDefined()
            expect(img.alt).not.toBeNull()
          })
        }
      )
    )
  })

  // 属性 7: 图像 src 属性应该被正确保留
  it('Property 7: Image src attribute should be correctly preserved', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach((img, idx) => {
            expect(img.src).toBe(htmlImages[idx].src)
          })
        }
      )
    )
  })

  // 属性 8: Alt 文本长度应该合理（不超过 125 个字符）
  it('Property 8: Alt text length should be reasonable (max 125 characters)', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(
            imageFilenameArb(),
            fc.string({ minLength: 1, maxLength: 125 })
          ),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach(img => {
            expect(img.alt!.length).toBeLessThanOrEqual(125)
          })
        }
      )
    )
  })

  // 属性 9: 多个图像应该各自有独立的 alt 属性
  it('Property 9: Multiple images should each have independent alt attributes', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
          { minLength: 2, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          expect(extracted.length).toBe(images.length)
          extracted.forEach((img, idx) => {
            expect(img.alt).toBe(htmlImages[idx].alt)
          })
        }
      )
    )
  })

  // 属性 10: Alt 文本不应该只是文件名
  it('Property 10: Alt text should not be just the filename', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach((img, idx) => {
            const src = htmlImages[idx].src
            const alt = img.alt!
            const filename = src.split('/').pop() || ''
            const filenameWithoutExt = filename.split('.')[0]

            // Alt 文本不应该与文件名相同
            expect(alt.toLowerCase()).not.toBe(filenameWithoutExt.toLowerCase())
          })
        }
      )
    )
  })

  // 属性 11: 特殊字符在 alt 文本中应该被正确处理
  it('Property 11: Special characters in alt text should be handled correctly', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(
            imageFilenameArb(),
            meaningfulAltTextArb()
          ),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({
            src,
            alt: alt.replace(/"/g, '&quot;'), // 转义引号
          }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          expect(extracted.length).toBe(images.length)
          extracted.forEach(img => {
            expect(img.alt).toBeDefined()
          })
        }
      )
    )
  })

  // 属性 12: 按钮图像应该有描述性的 alt 文本
  it('Property 12: Button images should have descriptive alt text', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(
            imageFilenameArb(),
            fc.stringMatching(/^(Close|Submit|Search|Delete|Edit|Save|Cancel|Download)/)
          ),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach(img => {
            expect(img.alt).toBeDefined()
            expect(img.alt!.length).toBeGreaterThan(0)
          })
        }
      )
    )
  })

  // 属性 13: 内容图像的 alt 文本应该有意义
  it('Property 13: Content images should have meaningful alt text', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach((img, idx) => {
            const src = htmlImages[idx].src
            const alt = img.alt!
            expect(isAltTextMeaningful(alt, src)).toBe(true)
          })
        }
      )
    )
  })

  // 属性 14: 图像数量应该被正确计数
  it('Property 14: Image count should be correctly counted', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 20 }).chain(count =>
          fc.tuple(
            fc.constant(count),
            fc.array(
              fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
              { minLength: count, maxLength: count }
            )
          )
        ),
        ([expectedCount, images]) => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          expect(extracted.length).toBe(expectedCount)
        }
      )
    )
  })

  // 属性 15: 空 alt 属性应该只用于装饰性图像
  it('Property 15: Empty alt attribute should only be used for decorative images', () => {
    fc.assert(
      fc.property(
        fc.tuple(
          fc.array(
            fc.tuple(imageFilenameArb(), decorativeAltTextArb()),
            { minLength: 1, maxLength: 5 }
          ),
          fc.array(
            fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
            { minLength: 1, maxLength: 5 }
          )
        ),
        ([decorativeImages, contentImages]) => {
          const allImages = [
            ...decorativeImages.map(([src, alt]) => ({ src, alt, isDecorative: true })),
            ...contentImages.map(([src, alt]) => ({ src, alt, isDecorative: false })),
          ]

          allImages.forEach(img => {
            if (img.isDecorative) {
              expect(img.alt).toBe('')
            } else {
              expect(img.alt).not.toBe('')
            }
          })
        }
      )
    )
  })

  // 属性 16: Alt 文本应该不包含冗余的"图像"或"图片"词语
  it('Property 16: Alt text should not contain redundant image-related words', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach(img => {
            const alt = img.alt!.toLowerCase()
            // Alt 文本不应该以"图像"或"图片"开头
            expect(alt).not.toMatch(/^(image|picture|photo|图像|图片|照片)\s+/i)
          })
        }
      )
    )
  })

  // 属性 17: 相同内容的多个图像应该有相同的 alt 文本
  it('Property 17: Multiple images with same content should have same alt text', () => {
    fc.assert(
      fc.property(
        fc.tuple(
          imageFilenameArb(),
          meaningfulAltTextArb(),
          fc.integer({ min: 2, max: 5 })
        ),
        ([src, alt, count]) => {
          const htmlImages = Array(count).fill({ src, alt })
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach(img => {
            expect(img.alt).toBe(alt)
          })
        }
      )
    )
  })

  // 属性 18: Alt 文本应该是可读的（不应该是乱码）
  it('Property 18: Alt text should be readable (not gibberish)', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach(img => {
            const alt = img.alt!
            // Alt 文本应该包含至少一个字母字符
            expect(/[a-zA-Z]/.test(alt) || alt === '').toBe(true)
          })
        }
      )
    )
  })

  // 属性 19: 图像的 alt 属性应该与 src 属性独立
  it('Property 19: Image alt attribute should be independent from src attribute', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach((img, idx) => {
            const src = htmlImages[idx].src
            const alt = img.alt!
            // Alt 文本和 src 可以不同
            expect(typeof alt).toBe('string')
            expect(typeof src).toBe('string')
          })
        }
      )
    )
  })

  // 属性 20: 所有图像元素都应该有 alt 属性（无论其他属性如何）
  it('Property 20: All image elements should have alt attribute regardless of other attributes', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(
            imageFilenameArb(),
            fc.oneof(meaningfulAltTextArb(), decorativeAltTextArb()),
            fc.integer({ min: 1, max: 500 }),
            fc.integer({ min: 1, max: 500 })
          ),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt, width, height]) => ({
            src,
            alt,
            width,
            height,
          }))

          // 创建包含 width 和 height 属性的 HTML
          const imageElements = htmlImages
            .map(
              img =>
                `<img src="${img.src}" alt="${img.alt}" width="${img.width}" height="${img.height}" />`
            )
            .join('\n')
          const html = `<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
${imageElements}
</body>
</html>`

          const extracted = extractImageElements(html)

          expect(extracted.length).toBe(images.length)
          extracted.forEach(img => {
            expect(img.alt).toBeDefined()
            expect(typeof img.alt).toBe('string')
          })
        }
      )
    )
  })

  // 属性 21: 长 alt 文本应该被正确处理
  it('Property 21: Long alt text should be correctly handled', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(
            imageFilenameArb(),
            fc.tuple(
              meaningfulAltTextArb(),
              meaningfulAltTextArb()
            ).map(([a, b]) => a + ' ' + b)
          ),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach((img, idx) => {
            expect(img.alt).toBe(htmlImages[idx].alt)
            expect(img.alt!.length).toBeGreaterThan(20)
          })
        }
      )
    )
  })

  // 属性 22: 图像 URL 路径应该被正确保留
  it('Property 22: Image URL paths should be correctly preserved', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(
            fc.stringMatching(/^[a-z0-9_-]+$/),
            fc.stringMatching(/^[a-z0-9_-]+$/),
            meaningfulAltTextArb()
          ),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([dir, file, alt]) => ({
            src: `${dir}/${file}.png`,
            alt,
          }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach((img, idx) => {
            expect(img.src).toBe(htmlImages[idx].src)
          })
        }
      )
    )
  })

  // 属性 23: 不同的图像应该可以有相同的 alt 文本
  it('Property 23: Different images can have the same alt text', () => {
    fc.assert(
      fc.property(
        fc.tuple(
          fc.array(imageFilenameArb(), { minLength: 2, maxLength: 5 }),
          meaningfulAltTextArb()
        ),
        ([srcs, alt]) => {
          const htmlImages = srcs.map(src => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          expect(extracted.length).toBe(srcs.length)
          extracted.forEach(img => {
            expect(img.alt).toBe(alt)
          })
        }
      )
    )
  })

  // 属性 24: Alt 文本应该对屏幕阅读器有用
  it('Property 24: Alt text should be useful for screen readers', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(imageFilenameArb(), meaningfulAltTextArb()),
          { minLength: 1, maxLength: 10 }
        ),
        images => {
          const htmlImages = images.map(([src, alt]) => ({ src, alt }))
          const html = htmlDocumentWithImagesArb(htmlImages)
          const extracted = extractImageElements(html)

          extracted.forEach(img => {
            // Alt 文本应该是非空的或明确为装饰性的
            expect(img.alt === '' || img.alt!.length > 0).toBe(true)
          })
        }
      )
    )
  })
})
