/**
 * DevOps Task Manager - Main Application File
 * This is the entry point for the Node.js application
 * 
 * The application serves the static files and can be extended with
 * backend functionality for task persistence, authentication, etc.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;

// Create HTTP server
const server = http.createServer((req, res) => {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // Handle API endpoints (can be extended for future features)
    if (req.url === '/api/tasks' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ tasks: [], message: 'Tasks retrieved from localStorage' }));
        return;
    }

    // Serve static files
    let filePath = req.url === '/' ? '/public/index.html' : `/public${req.url}`;
    filePath = path.join(__dirname, filePath);

    // Security: Prevent directory traversal
    const realPath = fs.realpathSync(path.join(__dirname, 'public'));
    if (!filePath.startsWith(realPath)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }

    // Check if file exists
    fs.stat(filePath, (err, stats) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'text/html' });
            res.end('<h1>404 - File Not Found</h1>');
            return;
        }

        // Serve the file
        const contentType = getContentType(filePath);
        res.writeHead(200, { 'Content-Type': contentType });
        fs.createReadStream(filePath).pipe(res);
    });
});

// Determine content type based on file extension
function getContentType(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    const types = {
        '.html': 'text/html; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
        '.js': 'text/javascript; charset=utf-8',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml'
    };
    return types[ext] || 'text/plain; charset=utf-8';
}

// Start server
server.listen(PORT, () => {
    console.log(`DevOps Task Manager Server is running on http://localhost:${PORT}`);
    console.log('Open your browser and navigate to http://localhost:3000');
});

// Handle server errors
server.on('error', (err) => {
    console.error('Server error:', err);
    process.exit(1);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\nShutting down server...');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});
