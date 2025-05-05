import { describe, expect, test } from 'vitest'
import { encryptKey } from 'server/utils/encryption/encrypt-key'

// filepath: server/utils/encryption/encrypt-key.test.ts

describe('encryptKey', () => {
  test('should return an object with iv and encrypted properties', () => {
    const encryptionKey = new Uint8Array(32) // Example 256-bit key
    const masterKey = new Uint8Array(32) // Example 256-bit key

    const result = encryptKey(encryptionKey, masterKey)

    expect(result).toHaveProperty('iv')
    expect(result).toHaveProperty('encrypted')
  })

  test('iv should be an array of length 16', () => {
    const encryptionKey = new Uint8Array(32)
    const masterKey = new Uint8Array(32)

    const { iv } = encryptKey(encryptionKey, masterKey)

    expect(Array.isArray(iv)).toBe(true)
    expect(iv).toHaveLength(16)
  })

  test('encrypted should be a Buffer or Uint8Array', () => {
    const encryptionKey = new Uint8Array(32)
    const masterKey = new Uint8Array(32)

    const { encrypted } = encryptKey(encryptionKey, masterKey)

    expect(encrypted instanceof Buffer || encrypted instanceof Uint8Array).toBe(true)
  })
})