import fs from 'node:fs';

const rawUrl = process.env.API_URL || 'http://127.0.0.1:8000';
const apiUrl = rawUrl.startsWith('http') ? rawUrl : `https://${rawUrl}`;

const content = `export const environment = {
  production: true,
  apiUrl: '${apiUrl.replace(/\/$/, '')}'
};
`;

fs.writeFileSync('src/environments/environment.prod.ts', content);
console.log(`Using API URL: ${apiUrl.replace(/\/$/, '')}`);
