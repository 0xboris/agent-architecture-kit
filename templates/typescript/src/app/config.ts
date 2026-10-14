/** Configuration from the environment. This is the one composition file where control flow is allowed. */
export interface Config {
  readonly port: number;
  readonly dataDir: string;
}

export function configFromEnvironment(): Config {
  return {
    port: Number(process.env['PORT'] ?? '8080'),
    dataDir: process.env['DATA_DIR'] ?? 'data',
  };
}
