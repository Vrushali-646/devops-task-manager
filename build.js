/**
 * DevOps Task Manager - Build Validation Script
 * This script is executed during the build process to validate that
 * all required application files are present and the application is ready for deployment.
 * 
 * Exit Code:
 *   0 = Build Success
 *   1 = Build Failed
 */

const fs = require('fs');
const path = require('path');

// Define required files for successful build
const requiredFiles = [
    'app.js',
    'package.json',
    'public/index.html',
    'script.js',
    'style.css'
];

console.log('╔════════════════════════════════════════════════════════╗');
console.log('║  DevOps Task Manager - Build Validation Process        ║');
console.log('╚════════════════════════════════════════════════════════╝\n');

console.log('Starting application build validation...\n');

let allFilesExist = true;
const results = [];

// Check each required file
for (const file of requiredFiles) {
    const filePath = path.join(__dirname, file);
    const exists = fs.existsSync(filePath);
    
    if (exists) {
        console.log(`✓ Found: ${file}`);
        results.push({ file, status: 'OK' });
    } else {
        console.error(`✗ Missing: ${file}`);
        results.push({ file, status: 'MISSING' });
        allFilesExist = false;
    }
}

console.log('\n' + '═'.repeat(56) + '\n');

// Validation result
if (allFilesExist) {
    console.log('✓ Application files validated successfully.');
    console.log('✓ All required files are present.');
    console.log('✓ Build validation completed without errors.\n');
    
    console.log('Build Summary:');
    console.log(`  - Total Files Checked: ${requiredFiles.length}`);
    console.log(`  - Files Found: ${results.filter(r => r.status === 'OK').length}`);
    console.log(`  - Files Missing: ${results.filter(r => r.status === 'MISSING').length}\n`);
    
    console.log('╔════════════════════════════════════════════════════════╗');
    console.log('║              Build Status: SUCCESS ✓                   ║');
    console.log('║                                                        ║');
    console.log('║  Application is ready for deployment                   ║');
    console.log('╚════════════════════════════════════════════════════════╝\n');
    
    process.exit(0);
} else {
    console.error('✗ Build validation failed. Missing required files:\n');
    results.forEach(result => {
        if (result.status === 'MISSING') {
            console.error(`  - ${result.file}`);
        }
    });
    
    console.log('\n' + '═'.repeat(56) + '\n');
    console.log('Build Summary:');
    console.log(`  - Total Files Checked: ${requiredFiles.length}`);
    console.log(`  - Files Found: ${results.filter(r => r.status === 'OK').length}`);
    console.log(`  - Files Missing: ${results.filter(r => r.status === 'MISSING').length}\n`);
    
    console.log('╔════════════════════════════════════════════════════════╗');
    console.log('║              Build Status: FAILURE ✗                   ║');
    console.log('║                                                        ║');
    console.log('║  Please ensure all required files are present          ║');
    console.log('╚════════════════════════════════════════════════════════╝\n');
    
    process.exit(1);
}
