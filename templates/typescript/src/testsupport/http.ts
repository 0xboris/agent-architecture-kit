import { createServer, type IncomingMessage, type ServerResponse } from 'node:http';
import type { AddressInfo } from 'node:net';

/** Starts a server on a free port for one test. Call close() when the test ends. */
export async function startTestServer(
  handle: (request: IncomingMessage, response: ServerResponse) => Promise<void>,
): Promise<{ url: string; close: () => Promise<void> }> {
  const server = createServer((request, response) => {
    void handle(request, response);
  });
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address() as AddressInfo;
  return {
    url: `http://127.0.0.1:${port}`,
    close: () => new Promise<void>((resolve, reject) => server.close((error) => (error ? reject(error) : resolve()))),
  };
}
