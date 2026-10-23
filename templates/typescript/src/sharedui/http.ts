import type { IncomingMessage, ServerResponse } from 'node:http';

export type Handler = (request: IncomingMessage, response: ServerResponse) => Promise<void>;

export interface Route {
  readonly method: string;
  readonly path: string;
  readonly handle: Handler;
}

const maxBodyBytes = 1 << 20;

export function sendJson(response: ServerResponse, status: number, body: unknown): void {
  response.writeHead(status, { 'content-type': 'application/json' });
  response.end(JSON.stringify(body));
}

export function sendError(
  response: ServerResponse,
  error: { readonly status: number; readonly code: string; readonly message: string },
): void {
  sendJson(response, error.status, { code: error.code, message: error.message });
}

/** Reads a JSON body. Unknown fields stay in the value, so newer clients can send fields this version ignores. */
export function readJson(request: IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    let size = 0;
    request.on('data', (chunk: Buffer) => {
      size += chunk.length;
      if (size > maxBodyBytes) {
        reject(new Error('The request body is too large.'));
        request.destroy();
        return;
      }
      chunks.push(chunk);
    });
    request.on('end', () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString('utf8')));
      } catch (error) {
        reject(new Error('The request body is not valid JSON.', { cause: error }));
      }
    });
    request.on('error', reject);
  });
}

export function createRouter(routes: readonly Route[], onError: (error: unknown) => void): Handler {
  return async (request, response) => {
    const path = new URL(request.url ?? '/', 'http://localhost').pathname;
    const route = routes.find((candidate) => candidate.method === request.method && candidate.path === path);
    if (route === undefined) {
      sendError(response, { status: 404, code: 'not_found', message: 'There is nothing at this path.' });
      return;
    }
    try {
      await route.handle(request, response);
    } catch (error) {
      onError(error);
      if (!response.headersSent) sendError(response, { status: 500, code: 'internal_error', message: 'Something went wrong.' });
    }
  };
}
