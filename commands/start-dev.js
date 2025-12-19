import path from 'node:path'
import { fileURLToPath } from 'node:url'
import concurrently from 'concurrently'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const projectRoot = path.resolve(__dirname, '..')

const { result } = concurrently([
    {
        command: 'bun run dev',
        name: 'UI',
        cwd: projectRoot,
        prefixColor: 'green',
    },
    {
        command: `uv run start.py`,
        name: 'APP',
        cwd: projectRoot,
        prefixColor: 'blue',
    },
])

result
    .then(() => {
        console.log('All development servers have started successfully.')
    })
    .catch((err) => {
        console.error('One of the development servers failed to start:', err)
    })
