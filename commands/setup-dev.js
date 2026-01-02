import { execSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const projectRoot = path.resolve(__dirname, '..')

const checkCommand = (command) => {
    try {
        execSync(`which ${command}`, { stdio: 'pipe' })
        return true
    } catch {
        return false
    }
}

const installBun = () => {
    console.log('\n')
    console.log('╭─────────────────────────────────────────╮')
    console.log('│  Installing Bun.js...                   │')
    console.log('╰─────────────────────────────────────────╯\n')

    try {
        if (process.platform === 'darwin') {
            execSync('curl -fsSL https://bun.sh/install | bash', {
                stdio: 'inherit',
            })
        } else if (process.platform === 'linux') {
            execSync('curl -fsSL https://bun.sh/install | bash', {
                stdio: 'inherit',
            })
        } else if (process.platform === 'win32') {
            execSync('powershell -c "irm bun.sh/install.ps1 | iex"', {
                stdio: 'inherit',
                shell: 'powershell.exe',
            })
        }
        console.log('✓ Bun.js installed successfully\n')
        return true
    } catch (error) {
        console.error('✗ Failed to install Bun.js:', error.message)
        return false
    }
}

const installUV = () => {
    console.log('\n')
    console.log('╭─────────────────────────────────────────╮')
    console.log('│  Installing UV...                       │')
    console.log('╰─────────────────────────────────────────╯\n')

    try {
        if (process.platform === 'darwin' || process.platform === 'linux') {
            execSync('curl -LsSf https://astral.sh/uv/install.sh | sh', {
                stdio: 'inherit',
            })
        } else if (process.platform === 'win32') {
            execSync(
                'powershell -c "irm https://astral.sh/uv/install.ps1 | iex"',
                {
                    stdio: 'inherit',
                    shell: 'powershell.exe',
                },
            )
        }
        console.log('✓ UV installed successfully\n')
        return true
    } catch (error) {
        console.error('✗ Failed to install UV:', error.message)
        return false
    }
}

const setup = () => {
    try {
        console.log('\n')
        console.log('╔═══════════════════════════════════════════╗')
        console.log('║  Development Environment Setup            ║')
        console.log('╚═══════════════════════════════════════════╝\n')

        // Check and install Bun if needed
        if (!checkCommand('bun')) {
            console.log('⚠ Bun.js not found. Installing...')
            if (!installBun()) {
                console.error(
                    '✗ Bun installation failed. Please install manually: https://bun.sh',
                )
                process.exit(1)
            }
        } else {
            console.log('✓ Bun.js is already installed\n')
        }

        // Check and install UV if needed
        if (!checkCommand('uv')) {
            console.log('⚠ UV not found. Installing...')
            if (!installUV()) {
                console.error(
                    '✗ UV installation failed. Please install manually: https://docs.astral.sh/uv/getting-started/installation/',
                )
                process.exit(1)
            }
        } else {
            console.log('✓ UV is already installed\n')
        }

        // Install Node dependencies with Bun
        console.log('╭─────────────────────────────────────────╮')
        console.log('│  Installing Node dependencies...        │')
        console.log('╰─────────────────────────────────────────╯\n')
        execSync('bun install', { stdio: 'inherit', cwd: projectRoot })
        console.log('\n✓ Node dependencies installed\n')

        // Install Python dependencies with UV
        console.log('╭─────────────────────────────────────────╮')
        console.log('│  Installing Python dependencies...      │')
        console.log('╰─────────────────────────────────────────╯\n')
        execSync('uv sync', { stdio: 'inherit', cwd: projectRoot })
        console.log('\n✓ Python dependencies installed\n')

        console.log('╭─────────────────────────────────────────╮')
        console.log('│  Setup Complete!                        │')
        console.log('╰─────────────────────────────────────────╯\n')
        console.log('You can now run "bun run start" to start the application.')
    } catch (error) {
        console.error('✗ An error occurred during setup:', error.message)
        process.exit(1)
    }
}

setup()
