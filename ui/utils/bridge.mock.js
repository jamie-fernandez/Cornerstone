/**
 * Mock implementation of the Python bridge API, used by `callApi` when
 * pywebview is not injected (plain-browser `vite dev`, Cypress E2E runs).
 *
 * Methods must mirror the public API class in `app/api.py` and resolve with
 * the same `{"status", "data"}` envelope the real bridge produces.
 */

const ok = (data) => Promise.resolve({ status: 'success', data })

export const mockApi = {
    quit: () => Promise.resolve(undefined),

    get_app_configuration: () =>
        ok({
            NAME: 'Cornerstone (mock)',
            SLUG: 'cornerstone',
            VERSION: '0.0.0',
            DEBUG: true,
            BASE_PATH: '/mock',
            HTML_PATH: 'http://localhost:5173',
        }),

    get_user_data: () =>
        ok({
            users: [
                { id: 1, name: 'John Doe', email: 'john@example.com' },
                { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
            ],
        }),

    get_system_info: () =>
        ok({
            platform: 'Mock',
            version: '0.0.0',
            machine: 'mock64',
            python_version: '0.0.0',
        }),

    get_database_path: () => ok({ path: '/mock/cornerstone.db' }),

    test_database_connection: () =>
        ok({ message: 'Database connection OK (mock)' }),

    get_system_stats: () =>
        ok({
            cpu_percent: 12.3,
            memory: {
                total: 16_000_000_000,
                available: 8_000_000_000,
                percent_used: 50,
            },
            disk: {
                total: 500_000_000_000,
                used: 250_000_000_000,
                percent_used: 50,
            },
        }),
}
