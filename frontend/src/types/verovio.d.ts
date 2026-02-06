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
declare module 'verovio/wasm' {
  const createVerovioModule: any;
  export default createVerovioModule;
}
