declare module 'verovio/esm' {
  export class VerovioToolkit {
    constructor(module: any);
    loadData(data: string): void;
    renderToSVG(page: number, options?: {
      scale?: number;
      adjustPageHeight?: boolean;
      [key: string]: any;
    }): string;
  }
}
