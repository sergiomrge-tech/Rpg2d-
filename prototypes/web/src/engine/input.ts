export type Action =
  | 'up' | 'down' | 'left' | 'right'
  | 'attack' | 'dodge' | 'interact'
  | 'skill1' | 'skill2' | 'skill3' | 'skill4'
  | 'menu' | 'confirm' | 'cancel' | 'tabL' | 'tabR';

const KEYMAP: Record<Action, string[]> = {
  up: ['ArrowUp', 'KeyW'],
  down: ['ArrowDown', 'KeyS'],
  left: ['ArrowLeft', 'KeyA'],
  right: ['ArrowRight', 'KeyD'],
  attack: ['KeyJ', 'KeyZ'],
  dodge: ['KeyK', 'KeyX', 'ShiftLeft', 'ShiftRight'],
  interact: ['KeyE', 'Space', 'Enter'],
  skill1: ['Digit1', 'KeyU'],
  skill2: ['Digit2', 'KeyI'],
  skill3: ['Digit3', 'KeyO'],
  skill4: ['Digit4', 'KeyP'],
  menu: ['Escape', 'Tab', 'KeyM'],
  confirm: ['Enter', 'Space', 'KeyJ', 'KeyZ', 'KeyE'],
  cancel: ['Escape', 'KeyK', 'KeyX', 'Backspace'],
  tabL: ['KeyQ', 'PageUp'],
  tabR: ['KeyR', 'PageDown'],
};

// Gamepad (layout "standard")
const PAD: Partial<Record<Action, number[]>> = {
  attack: [2],
  dodge: [1],
  interact: [0],
  confirm: [0, 2],
  cancel: [1],
  skill1: [3],
  skill2: [5],
  skill3: [4],
  skill4: [7],
  menu: [9, 8],
  tabL: [4],
  tabR: [5],
  up: [12],
  down: [13],
  left: [14],
  right: [15],
};

class InputManager {
  private keys = new Set<string>();
  private virt = new Set<Action>();
  private evPress = new Set<Action>();
  private padHeld = new Set<Action>();
  private held = new Set<Action>();
  private prev = new Set<Action>();
  private press = new Set<Action>();
  private lastPress = new Map<Action, number>();
  private clock = 0;
  private holdT = new Map<Action, number>();
  private repNext = new Map<Action, number>();
  anyKey = false;
  padAxis = { x: 0, y: 0 };
  onFirstGesture: (() => void)[] = [];

  init() {
    window.addEventListener('keydown', (e) => {
      if (e.code.startsWith('Arrow') || e.code === 'Space' || e.code === 'Tab') e.preventDefault();
      if (!this.keys.has(e.code)) for (const act of Object.keys(KEYMAP) as Action[]) if (KEYMAP[act].includes(e.code)) this.evPress.add(act);
      this.keys.add(e.code);
      this.anyKey = true;
      this.gesture();
    });
    window.addEventListener('keyup', (e) => this.keys.delete(e.code));
    window.addEventListener('blur', () => {
      this.keys.clear();
      this.virt.clear();
    });
    window.addEventListener('pointerdown', () => this.gesture());
  }

  private gesture() {
    if (this.onFirstGesture.length) {
      const fns = this.onFirstGesture;
      this.onFirstGesture = [];
      fns.forEach((f) => f());
    }
  }

  setVirtual(a: Action, on: boolean) {
    if (on) { if (!this.virt.has(a)) this.evPress.add(a); this.virt.add(a); }
    else this.virt.delete(a);
  }

  /** Call once per frame before updates. */
  poll(dt: number) {
    this.clock += dt;
    this.padHeld.clear();
    this.padAxis.x = 0;
    this.padAxis.y = 0;
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    for (const p of pads) {
      if (!p) continue;
      for (const [act, btns] of Object.entries(PAD) as [Action, number[]][]) {
        if (btns.some((b) => p.buttons[b]?.pressed)) this.padHeld.add(act);
      }
      const ax = p.axes[0] ?? 0;
      const ay = p.axes[1] ?? 0;
      if (Math.hypot(ax, ay) > 0.3) {
        this.padAxis.x = ax;
        this.padAxis.y = ay;
        if (ax < -0.5) this.padHeld.add('left');
        if (ax > 0.5) this.padHeld.add('right');
        if (ay < -0.5) this.padHeld.add('up');
        if (ay > 0.5) this.padHeld.add('down');
      }
    }
    this.prev = this.held;
    this.held = new Set<Action>();
    for (const act of Object.keys(KEYMAP) as Action[]) {
      if (KEYMAP[act].some((k) => this.keys.has(k)) || this.virt.has(act) || this.padHeld.has(act)) {
        this.held.add(act);
      }
    }
    for (const a of this.evPress) this.held.add(a);
    this.evPress.clear();
    for (const a of Object.keys(KEYMAP) as Action[]) {
      if (this.held.has(a)) this.holdT.set(a, (this.holdT.get(a) ?? 0) + dt);
      else { this.holdT.delete(a); this.repNext.delete(a); }
    }
    this.press = new Set<Action>();
    for (const a of this.held) {
      if (!this.prev.has(a)) {
        this.press.add(a);
        this.lastPress.set(a, this.clock);
      }
    }
  }

  down(a: Action) {
    return this.held.has(a);
  }
  /** True on press, then repeats while held (for menus). */
  rep(a: Action) {
    if (this.press.has(a)) { this.repNext.set(a, 0.32); return true; }
    const h = this.holdT.get(a);
    if (h === undefined) return false;
    const n = this.repNext.get(a);
    if (n !== undefined && h >= n) { this.repNext.set(a, n + 0.09); return true; }
    return false;
  }
  pressed(a: Action) {
    return this.press.has(a);
  }
  /** True if pressed within the last `win` seconds and not consumed. */
  buffered(a: Action, win = 0.15) {
    const t = this.lastPress.get(a);
    return t !== undefined && this.clock - t <= win;
  }
  consume(a: Action) {
    this.lastPress.delete(a);
  }
  /** Swallow this frame's press (so a modal opened by it does not react to the same key). */
  eat(...as: Action[]) {
    for (const a of as) { this.press.delete(a); this.lastPress.delete(a); this.repNext.delete(a); }
  }
  clearAll() {
    this.lastPress.clear();
  }
  axis() {
    let x = 0;
    let y = 0;
    if (this.down('left')) x -= 1;
    if (this.down('right')) x += 1;
    if (this.down('up')) y -= 1;
    if (this.down('down')) y += 1;
    if (this.padAxis.x || this.padAxis.y) {
      x = this.padAxis.x;
      y = this.padAxis.y;
    }
    const m = Math.hypot(x, y);
    if (m > 1) {
      x /= m;
      y /= m;
    }
    return { x, y };
  }
}

export const Input = new InputManager();

/** On-screen controls for touch devices. */
export function setupTouchControls(root: HTMLElement) {
  const coarse = window.matchMedia('(pointer: coarse)').matches || 'ontouchstart' in window;
  if (!coarse) return;
  const layer = document.createElement('div');
  layer.className = 'touch';
  root.appendChild(layer);

  const stick = document.createElement('div');
  stick.className = 'stick';
  const knob = document.createElement('div');
  knob.className = 'knob';
  stick.appendChild(knob);
  layer.appendChild(stick);

  const place = () => {
    const s = Math.min(window.innerWidth, window.innerHeight);
    const sz = Math.round(s * 0.34);
    stick.style.width = stick.style.height = sz + 'px';
    stick.style.left = Math.round(s * 0.05) + 'px';
    stick.style.bottom = Math.round(s * 0.07) + 'px';
    const b = Math.round(s * 0.14);
    for (const el of layer.querySelectorAll<HTMLElement>('.btn')) {
      const k = el.dataset.k!.split(',').map(Number);
      el.style.width = el.style.height = Math.round(b * k[2]) + 'px';
      el.style.right = Math.round(s * k[0] / 100) + 'px';
      el.style.bottom = Math.round(s * k[1] / 100) + 'px';
    }
  };

  let stickId = -1;
  const upd = (e: PointerEvent) => {
    const r = stick.getBoundingClientRect();
    const cx = r.left + r.width / 2;
    const cy = r.top + r.height / 2;
    let dx = (e.clientX - cx) / (r.width / 2);
    let dy = (e.clientY - cy) / (r.height / 2);
    const m = Math.hypot(dx, dy);
    if (m > 1) {
      dx /= m;
      dy /= m;
    }
    knob.style.transform = `translate(${dx * 50}%, ${dy * 50}%)`;
    Input.setVirtual('left', dx < -0.3);
    Input.setVirtual('right', dx > 0.3);
    Input.setVirtual('up', dy < -0.3);
    Input.setVirtual('down', dy > 0.3);
  };
  stick.addEventListener('pointerdown', (e) => {
    stickId = e.pointerId;
    stick.setPointerCapture(e.pointerId);
    upd(e);
  });
  stick.addEventListener('pointermove', (e) => {
    if (e.pointerId === stickId) upd(e);
  });
  const endStick = (e: PointerEvent) => {
    if (e.pointerId !== stickId) return;
    stickId = -1;
    knob.style.transform = '';
    (['left', 'right', 'up', 'down'] as Action[]).forEach((a) => Input.setVirtual(a, false));
  };
  stick.addEventListener('pointerup', endStick);
  stick.addEventListener('pointercancel', endStick);

  // [right%, bottom%, size multiplier] relative to min screen side
  const defs: [string, Action[], string][] = [
    ['⚔', ['attack', 'confirm'], '6,16,1.15'],
    ['⤵', ['dodge', 'cancel'], '19,8,0.9'],
    ['E', ['interact'], '19,24,0.8'],
    ['1', ['skill1'], '4,34,0.75'],
    ['2', ['skill2'], '14,40,0.75'],
    ['3', ['skill3'], '26,40,0.75'],
    ['4', ['skill4'], '36,32,0.75'],
    ['☰', ['menu'], '2,86,0.7'],
  ];
  for (const [label, acts, k] of defs) {
    const b = document.createElement('div');
    b.className = 'btn';
    b.textContent = label;
    b.dataset.k = k;
    const on = (v: boolean) => {
      acts.forEach((a) => Input.setVirtual(a, v));
      b.classList.toggle('on', v);
    };
    b.addEventListener('pointerdown', (e) => {
      b.setPointerCapture(e.pointerId);
      on(true);
    });
    b.addEventListener('pointerup', () => on(false));
    b.addEventListener('pointercancel', () => on(false));
    layer.appendChild(b);
  }
  place();
  window.addEventListener('resize', place);
}
