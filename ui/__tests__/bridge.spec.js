import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const success = (data) => Promise.resolve({ status: 'success', data })

function injectApi(api) {
    window.pywebview = { api }
}

/** Import the bridge module fresh (its resolved-API cache is module state). */
async function freshBridge() {
    return await import('@/utils/bridge.js')
}

beforeEach(() => {
    vi.resetModules()
})

afterEach(() => {
    delete window.pywebview
    vi.useRealTimers()
    vi.restoreAllMocks()
})

describe('callApi', () => {
    it('returns the unwrapped data payload on success', async () => {
        injectApi({ get_user_data: () => success({ users: [] }) })
        const { callApi } = await freshBridge()

        await expect(callApi('get_user_data')).resolves.toEqual({ users: [] })
    })

    it('forwards arguments to the bridge method', async () => {
        const greet = vi.fn((name) => success(`Hello, ${name}!`))
        injectApi({ greet })
        const { callApi } = await freshBridge()

        await expect(callApi('greet', 'Ada')).resolves.toBe('Hello, Ada!')
        expect(greet).toHaveBeenCalledWith('Ada')
    })

    it('throws BridgeError with the Python message on an error envelope', async () => {
        injectApi({
            fails: () =>
                Promise.resolve({
                    status: 'error',
                    message: 'safe, user-facing message',
                }),
        })
        const { callApi, BridgeError } = await freshBridge()

        await expect(callApi('fails')).rejects.toThrow(BridgeError)
        await expect(callApi('fails')).rejects.toThrow(
            'safe, user-facing message',
        )
    })

    it('throws BridgeUnavailableError for unknown bridge methods', async () => {
        injectApi({})
        const { callApi, BridgeUnavailableError } = await freshBridge()

        await expect(callApi('nope')).rejects.toThrow(BridgeUnavailableError)
    })

    it('waits for the pywebviewready event when the bridge is injected late', async () => {
        const { callApi } = await freshBridge()
        const pending = callApi('get_system_info')

        injectApi({ get_system_info: () => success({ platform: 'Darwin' }) })
        window.dispatchEvent(new Event('pywebviewready'))

        await expect(pending).resolves.toEqual({ platform: 'Darwin' })
    })

    it('falls back to the mock API when pywebview is never injected', async () => {
        vi.useFakeTimers()
        const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
        const { callApi } = await freshBridge()

        const pending = callApi('get_system_info')
        await vi.advanceTimersByTimeAsync(1_500)

        await expect(pending).resolves.toMatchObject({ platform: 'Mock' })
        expect(warn).toHaveBeenCalled()
    })
})

describe('waitForBridge', () => {
    it('resolves immediately when the bridge is already injected', async () => {
        const api = { ping: () => success('pong') }
        injectApi(api)
        const { waitForBridge } = await freshBridge()

        await expect(waitForBridge()).resolves.toBe(api)
    })

    it('rejects with BridgeUnavailableError after the timeout', async () => {
        const { waitForBridge, BridgeUnavailableError } = await freshBridge()

        await expect(waitForBridge(50)).rejects.toThrow(BridgeUnavailableError)
    })
})
