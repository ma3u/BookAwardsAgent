const config = require('./config');

// This will throw an error if any required environment variables are missing
console.log('Configuration test successful!');
console.log('Airtable Table:', config.airtable.tableName);
