import type { MapDef } from './map';

type Builder = () => MapDef;
export const MAP_BUILDERS: Record<string, Builder> = {};
export function registerMap(id: string, fn: Builder) { MAP_BUILDERS[id] = fn; }

const cache = new Map<string, MapDef>();
export function getMap(id: string): MapDef {
  // rebuild each time so spawn/object state resets; builders are deterministic
  const fn = MAP_BUILDERS[id];
  if (!fn) throw new Error('Mapa desconhecido: ' + id);
  const m = fn();
  cache.set(id, m);
  return m;
}
