import { spawn } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const projectRoot = path.resolve(__dirname, '..')

const buildBackend = () => {
    const pyinstallerProcess = spawn(
        'python',
        [path.join(projectRoot, 'commands', 'build-pyinstaller.py')],
        {
            stdio: 'inherit',
        },
    )

    pyinstallerProcess.on('close', (code) => {
        if (code !== 0) {
            console.error('PyInstaller build failed.')
            process.exit(1)
        } else {
            console.log('Backend build completed successfully.')
        }
    })
}

buildBackend()
