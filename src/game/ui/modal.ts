export abstract class Modal<T = void> {
  done = false;
  result!: T;
  resolver?: (v: T) => void;
  /** If true the world simulation is paused while this modal is open. */
  pauses = true;
  abstract update(dt: number): void;
  abstract drawUI(u: CanvasRenderingContext2D): void;
  close(v?: T) {
    this.done = true;
    this.result = v as T;
    this.resolver?.(this.result);
  }
}
