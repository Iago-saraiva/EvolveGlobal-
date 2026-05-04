// config.js
const ENV = {
    development: {
        API_URL: 'http://localhost:5000/api'
    },
    production: {
        API_URL: 'https://evolveglobal-api.onrender.com/api'
    }
};

const currentEnv = window.location.hostname === 'localhost' ? 'development' : 'production';
const API_URL = ENV[currentEnv].API_URL;