import { fileURLToPath } from 'node:url'
import { configDefaults, defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
    viteConfig,
    defineConfig({
        test: {
            environment: 'jsdom',
            exclude: [
                ...configDefaults.exclude,
                'e2e/**',
                '.gitlab-ci-local/**',
            ],
            root: fileURLToPath(new URL('./', import.meta.url)),
            coverage: {
                // istanbul (not v8): v8 coverage needs Node's inspector APIs, but CI
                // runs vitest under the Bun runtime (oven/bun image has no Node).
                // Istanbul is instrumentation-based and works under both runtimes.
                provider: 'istanbul',
                // text: console summary; cobertura: consumed by GitLab's MR coverage widget.
                // Inert unless `--coverage` is passed (CI only).
                reporter: ['text', 'cobertura'],
            },
        },
    }),
)
