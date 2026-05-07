import { describe, it, expect, beforeEach } from 'vitest'
import { authAPI } from '../src/api/auth'

describe('Authentication API', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })

  it('should have register method', () => {
    expect(authAPI.register).toBeDefined()
  })

  it('should have login method', () => {
    expect(authAPI.login).toBeDefined()
  })

  it('should have logout method', () => {
    expect(authAPI.logout).toBeDefined()
  })

  it('should have getCurrentUser method', () => {
    expect(authAPI.getCurrentUser).toBeDefined()
  })

  it('should have refreshToken method', () => {
    expect(authAPI.refreshToken).toBeDefined()
  })

  it('should have changePassword method', () => {
    expect(authAPI.changePassword).toBeDefined()
  })
})
