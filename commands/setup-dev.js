import { execSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// Convert import.meta.url to a file path
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const projectRoot = path.resolve(__dirname, '..')

const checkVirtualEnvironment = () => {
    const venvPath = path.join(projectRoot, '.venv')
    const pythonExecutable =
        process.platform === 'win32'
            ? path.join(venvPath, 'Scripts', 'python.exe')
            : path.join(venvPath, 'bin', 'python3')

    return {
        exists: fs.existsSync(venvPath),
        pythonExecutable,
    }
}

const createVirtualEnvironment = () => {
    console.log('Creating Python virtual environment...')
    execSync('python3 -m venv .venv', { stdio: 'inherit', cwd: projectRoot })
}

const activateVirtualEnvironment = () => {
    const { pythonExecutable } = checkVirtualEnvironment()

    // Set environment variables to simulate activation
    const venvPath = path.join(projectRoot, '.venv')
    const binPath =
        process.platform === 'win32'
            ? path.join(venvPath, 'Scripts')
            : path.join(venvPath, 'bin')

    // Prepend venv bin directory to PATH
    process.env.PATH = `${binPath}${path.delimiter}${process.env.PATH}`
    process.env.VIRTUAL_ENV = venvPath

    // Remove PYTHONHOME if it exists to avoid conflicts
    delete process.env.PYTHONHOME

    console.log('✓ Virtual environment activated')
    return pythonExecutable
}

const setup = () => {
    try {
        console.log('Installing root Node dependencies...')
        execSync('bun install', { stdio: 'inherit', cwd: projectRoot })

        console.log('Setting up Python virtual environment...')

        const venvStatus = checkVirtualEnvironment()
        let pythonExecutable

        if (venvStatus.exists) {
            console.log('✓ Virtual environment already exists')
            pythonExecutable = activateVirtualEnvironment()
        } else {
            createVirtualEnvironment()
            pythonExecutable = activateVirtualEnvironment()
        }

        console.log('Installing Python dependencies...')
        execSync(`"${pythonExecutable}" -m pip install -r requirements.txt`, {
            stdio: 'inherit',
            cwd: projectRoot,
            env: process.env,
        })

        console.log('Development environment setup is complete! 🎉')
        console.log(
            'You can now run "npm run start:dev" to start the application.',
        )
        console.log(
            '\nNote: The virtual environment has been activated for this process.',
        )
        console.log('To manually activate it in your shell, run:')

        if (process.platform === 'win32') {
            console.log('  .venv\\Scripts\\activate')
        } else {
            console.log('  source .venv/bin/activate')
        }
    } catch (error) {
        console.error('An error occurred during setup:', error.message)
        process.exit(1)
    }
}

setup()
