/**
 * Client for the Python bridge (pywebview).
 *
 * The Python backend exposes methods on `window.pywebview.api`, but that
 * object is injected asynchronously — never touch it directly. Always go
 * through `callApi`, which waits for the `pywebviewready` event, unwraps the
 * `{"status", "data"|"message"}` envelope produced by `@bridge_method`, and
 * throws on error envelopes.
 *
 * When pywebview is not present at all (plain-browser `vite dev`, Cypress
 * E2E runs), calls fall back to the mock implementation in `bridge.mock.js`.
 */

const BRIDGE_READY_EVENT = 'pywebviewready'
const BRIDGE_READY_TIMEOUT_MS = 10_000
const MOCK_FALLBACK_DELAY_MS = 1_000

/** A user-facing error returned by a Python bridge method (error envelope). */
export class BridgeError extends Error {
    constructor(message) {
        super(message)
        this.name = 'BridgeError'
    }
}

/** The bridge itself is missing, slow to inject, or lacks the requested method. */
export class BridgeUnavailableError extends Error {
    constructor(message = 'Python bridge is unavailable') {
        super(message)
        this.name = 'BridgeUnavailableError'
    }
}

function getInjectedApi() {
    return typeof window === 'undefined'
        ? null
        : (window.pywebview?.api ?? null)
}

let readinessPromise = null

/**
 * Resolve with `window.pywebview.api`, waiting for the `pywebviewready`
 * event if the bridge has not been injected yet.
 *
 * @param {number} timeoutMs Maximum time to wait before giving up.
 * @returns {Promise<object>} The injected `window.pywebview.api` object.
 * @throws {BridgeUnavailableError} When the bridge is not ready in time.
 */
export function waitForBridge(timeoutMs = BRIDGE_READY_TIMEOUT_MS) {
    const api = getInjectedApi()
    if (api) {
        return Promise.resolve(api)
    }

    readinessPromise ??= new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
            readinessPromise = null // Allow retry after a timed-out wait.
            reject(
                new BridgeUnavailableError(
                    `pywebview bridge not ready after ${timeoutMs}ms`,
                ),
            )
        }, timeoutMs)

        window.addEventListener(
            BRIDGE_READY_EVENT,
            () => {
                clearTimeout(timer)
                resolve(getInjectedApi())
            },
            { once: true },
        )
    })

    return readinessPromise
}

let apiPromise = null

/**
 * Resolve with the real bridge API when pywebview is present, otherwise with
 * the mock API after a short grace period. The result is cached, so the
 * grace period is only paid on the first call.
 */
function resolveApi() {
    apiPromise ??= (async () => {
        try {
            return await waitForBridge(MOCK_FALLBACK_DELAY_MS)
        } catch {
            const { mockApi } = await import('@/utils/bridge.mock.js')
            console.warn(
                '[bridge] pywebview not detected, falling back to mock API',
            )
            return mockApi
        }
    })()
    return apiPromise
}

/**
 * Call a Python bridge method and return its unwrapped `data` payload.
 *
 * @param {string} method Public method name of the API class in `app/api.py`.
 * @param {...*} args Arguments forwarded to the Python method.
 * @returns {Promise<*>} The `data` field of the success envelope.
 * @throws {BridgeError} When Python returns an error envelope.
 * @throws {BridgeUnavailableError} When the method does not exist on the bridge.
 *
 * @example
 * try {
 *     const stats = await callApi('get_system_stats')
 * } catch (error) {
 *     if (error instanceof BridgeError) showSnackbar(error.message)
 *     else throw error
 * }
 */
export async function callApi(method, ...args) {
    const api = await resolveApi()
    if (typeof api[method] !== 'function') {
        throw new BridgeUnavailableError(
            `Bridge method "${method}" is not available`,
        )
    }
    const response = await api[method](...args)
    if (response?.status === 'error') {
        throw new BridgeError(response.message ?? 'Unknown bridge error')
    }
    return response?.data
}
