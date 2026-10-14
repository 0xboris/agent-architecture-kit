import { createServer } from 'node:http';
import { configFromEnvironment } from './config.ts';
import { createApp } from './container.ts';
import { liveDependencies } from './live.ts';

const config = configFromEnvironment();
const app = createApp(liveDependencies(config));

createServer((request, response) => {
  void app.handle(request, response);
}).listen(config.port);
