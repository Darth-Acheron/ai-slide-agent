const fs = require('fs');
const content = fs.readFileSync('web/templates/index.html', 'utf8');
const scriptMatch = content.match(/<script>([\s\S]*?)<\/script>/);
if (scriptMatch) {
    try {
        new Function(scriptMatch[1]);
        console.log("Syntax is OK!");
    } catch(e) {
        console.log("Syntax Error: " + e.message);
    }
}
