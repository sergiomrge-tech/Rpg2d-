import { Rng } from './util';

const mtof = (m: number) => 440 * Math.pow(2, (m - 69) / 12);

interface Theme {
  bpm: number;
  root: number; // midi root
  scale: number[];
  prog: number[]; // chord roots as scale degrees
  lead: OscillatorType;
  leadVol: number;
  density: number; // melody note probability
  drums: 0 | 1 | 2;
  arp: boolean;
  seed: number;
  octave?: number;
}

const MAJ = [0, 2, 4, 5, 7, 9, 11];
const MIN = [0, 2, 3, 5, 7, 8, 10];
const PENT = [0, 2, 4, 7, 9];
const DORIAN = [0, 2, 3, 5, 7, 9, 10];
const PHRYG = [0, 1, 3, 5, 7, 8, 10];

export const THEMES: Record<string, Theme> = {
  title: { bpm: 84, root: 57, scale: MIN, prog: [0, 5, 2, 6], lead: 'triangle', leadVol: 0.2, density: 0.55, drums: 0, arp: true, seed: 11 },
  village: { bpm: 96, root: 62, scale: PENT, prog: [0, 3, 4, 3], lead: 'triangle', leadVol: 0.22, density: 0.65, drums: 1, arp: true, seed: 21 },
  forest: { bpm: 88, root: 57, scale: DORIAN, prog: [0, 6, 3, 4], lead: 'triangle', leadVol: 0.2, density: 0.5, drums: 1, arp: true, seed: 31 },
  cave: { bpm: 72, root: 52, scale: PHRYG, prog: [0, 0, 5, 4], lead: 'sine', leadVol: 0.2, density: 0.35, drums: 0, arp: true, seed: 41 },
  battle: { bpm: 142, root: 57, scale: MIN, prog: [0, 5, 6, 4], lead: 'square', leadVol: 0.1, density: 0.75, drums: 2, arp: true, seed: 51 },
  boss: { bpm: 156, root: 52, scale: PHRYG, prog: [0, 1, 0, 4], lead: 'sawtooth', leadVol: 0.09, density: 0.85, drums: 2, arp: true, seed: 61 },
  sad: { bpm: 64, root: 60, scale: MIN, prog: [0, 5, 3, 4], lead: 'sine', leadVol: 0.24, density: 0.4, drums: 0, arp: false, seed: 71 },
  victory: { bpm: 120, root: 60, scale: MAJ, prog: [0, 3, 4, 0], lead: 'square', leadVol: 0.1, density: 0.8, drums: 1, arp: true, seed: 81 },
};

class AudioEngine {
  ctx: AudioContext | null = null;
  master!: GainNode;
  musicGain!: GainNode;
  sfxGain!: GainNode;
  noiseBuf!: AudioBuffer;
  current = '';
  private timer: number | null = null;
  private step = 0;
  private nextTime = 0;
  musicVol = 0.5;
  sfxVol = 0.7;
  muted = false;

  /** Must be called from a user gesture. */
  unlock() {
    if (this.ctx) {
      if (this.ctx.state === 'suspended') void this.ctx.resume();
      return;
    }
    const AC = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    if (!AC) return;
    this.ctx = new AC();
    this.master = this.ctx.createGain();
    this.master.gain.value = this.muted ? 0 : 0.8;
    this.master.connect(this.ctx.destination);
    this.musicGain = this.ctx.createGain();
    this.musicGain.gain.value = this.musicVol * 0.5;
    this.musicGain.connect(this.master);
    this.sfxGain = this.ctx.createGain();
    this.sfxGain.gain.value = this.sfxVol;
    this.sfxGain.connect(this.master);
    const len = this.ctx.sampleRate;
    this.noiseBuf = this.ctx.createBuffer(1, len, this.ctx.sampleRate);
    const d = this.noiseBuf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    if (this.current) {
      const c = this.current;
      this.current = '';
      this.music(c);
    }
  }

  setVolumes(music: number, sfx: number) {
    this.musicVol = music;
    this.sfxVol = sfx;
    if (this.ctx) {
      this.musicGain.gain.value = music * 0.5;
      this.sfxGain.gain.value = sfx;
    }
  }

  toggleMute() {
    this.muted = !this.muted;
    if (this.ctx) this.master.gain.value = this.muted ? 0 : 0.8;
  }

  // ---------- low level ----------
  private tone(o: {
    type?: OscillatorType; f0: number; f1?: number; dur: number; vol?: number; t?: number;
    dest?: AudioNode; attack?: number; lp?: number; detune?: number;
  }) {
    const c = this.ctx!;
    const t = o.t ?? c.currentTime;
    const osc = c.createOscillator();
    const g = c.createGain();
    osc.type = o.type ?? 'square';
    osc.frequency.setValueAtTime(o.f0, t);
    if (o.f1) osc.frequency.exponentialRampToValueAtTime(Math.max(1, o.f1), t + o.dur);
    if (o.detune) osc.detune.value = o.detune;
    const v = o.vol ?? 0.2;
    const a = o.attack ?? 0.005;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(v, t + a);
    g.gain.exponentialRampToValueAtTime(0.0001, t + o.dur);
    let node: AudioNode = osc;
    if (o.lp) {
      const f = c.createBiquadFilter();
      f.type = 'lowpass';
      f.frequency.value = o.lp;
      osc.connect(f);
      node = f;
    }
    node.connect(g);
    g.connect(o.dest ?? this.sfxGain);
    osc.start(t);
    osc.stop(t + o.dur + 0.05);
  }

  private noise(o: { dur: number; vol?: number; t?: number; hp?: number; lp?: number; dest?: AudioNode; f1?: number }) {
    const c = this.ctx!;
    const t = o.t ?? c.currentTime;
    const src = c.createBufferSource();
    src.buffer = this.noiseBuf;
    const g = c.createGain();
    g.gain.setValueAtTime(o.vol ?? 0.2, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + o.dur);
    let node: AudioNode = src;
    if (o.hp) {
      const f = c.createBiquadFilter();
      f.type = 'highpass';
      f.frequency.value = o.hp;
      node.connect(f);
      node = f;
    }
    if (o.lp) {
      const f = c.createBiquadFilter();
      f.type = 'lowpass';
      f.frequency.setValueAtTime(o.lp, t);
      if (o.f1) f.frequency.exponentialRampToValueAtTime(o.f1, t + o.dur);
      node.connect(f);
      node = f;
    }
    node.connect(g);
    g.connect(o.dest ?? this.sfxGain);
    src.start(t);
    src.stop(t + o.dur + 0.05);
  }

  // ---------- SFX ----------
  private lastSfx = new Map<string, number>();
  sfx(name: string) {
    if (!this.ctx || this.muted) return;
    const now = this.ctx.currentTime;
    const last = this.lastSfx.get(name) ?? 0;
    if (now - last < 0.03) return;
    this.lastSfx.set(name, now);
    const T = this.tone.bind(this);
    const N = this.noise.bind(this);
    switch (name) {
      case 'swing': N({ dur: 0.12, vol: 0.18, hp: 800, lp: 6000, f1: 1500 }); T({ type: 'triangle', f0: 380, f1: 160, dur: 0.1, vol: 0.08 }); break;
      case 'hit': N({ dur: 0.1, vol: 0.28, lp: 3000, f1: 400 }); T({ type: 'square', f0: 220, f1: 80, dur: 0.1, vol: 0.14 }); break;
      case 'crit': N({ dur: 0.18, vol: 0.32, lp: 5000, f1: 300 }); T({ type: 'sawtooth', f0: 700, f1: 100, dur: 0.18, vol: 0.14 }); T({ type: 'square', f0: 1200, f1: 600, dur: 0.08, vol: 0.08 }); break;
      case 'hurt': T({ type: 'sawtooth', f0: 300, f1: 70, dur: 0.22, vol: 0.18 }); N({ dur: 0.12, vol: 0.2, lp: 2000 }); break;
      case 'dodge': N({ dur: 0.18, vol: 0.14, hp: 1200, lp: 7000, f1: 2500 }); break;
      case 'fire': N({ dur: 0.3, vol: 0.2, lp: 2500, f1: 500 }); T({ type: 'sawtooth', f0: 200, f1: 520, dur: 0.25, vol: 0.1 }); break;
      case 'ice': T({ type: 'triangle', f0: 1500, f1: 700, dur: 0.25, vol: 0.14 }); T({ type: 'sine', f0: 2200, f1: 1100, dur: 0.3, vol: 0.1 }); break;
      case 'bolt': T({ type: 'sawtooth', f0: 1800, f1: 120, dur: 0.22, vol: 0.14 }); N({ dur: 0.2, vol: 0.2, hp: 2000 }); break;
      case 'heal': [523, 659, 784, 1047].forEach((f, i) => T({ type: 'triangle', f0: f, dur: 0.25, vol: 0.14, t: this.ctx!.currentTime + i * 0.06 })); break;
      case 'buff': T({ type: 'triangle', f0: 400, f1: 900, dur: 0.3, vol: 0.14 }); T({ type: 'sine', f0: 600, f1: 1200, dur: 0.3, vol: 0.1 }); break;
      case 'shield': T({ type: 'sine', f0: 300, f1: 600, dur: 0.35, vol: 0.18 }); T({ type: 'triangle', f0: 900, dur: 0.2, vol: 0.08 }); break;
      case 'slam': N({ dur: 0.4, vol: 0.4, lp: 900, f1: 100 }); T({ type: 'sine', f0: 120, f1: 40, dur: 0.4, vol: 0.3 }); break;
      case 'explosion': N({ dur: 0.6, vol: 0.4, lp: 3000, f1: 80 }); T({ type: 'sine', f0: 100, f1: 30, dur: 0.5, vol: 0.3 }); break;
      case 'pickup': T({ type: 'square', f0: 880, dur: 0.06, vol: 0.1 }); T({ type: 'square', f0: 1320, dur: 0.1, vol: 0.1, t: this.ctx.currentTime + 0.06 }); break;
      case 'coin': T({ type: 'square', f0: 988, dur: 0.05, vol: 0.09 }); T({ type: 'square', f0: 1319, dur: 0.12, vol: 0.09, t: this.ctx.currentTime + 0.05 }); break;
      case 'chest': [392, 523, 659, 784, 1047].forEach((f, i) => T({ type: 'square', f0: f, dur: 0.14, vol: 0.1, t: this.ctx!.currentTime + i * 0.07 })); break;
      case 'levelup': [523, 659, 784, 1047, 784, 1047, 1319].forEach((f, i) => T({ type: 'square', f0: f, dur: 0.18, vol: 0.12, t: this.ctx!.currentTime + i * 0.08 })); break;
      case 'ui_move': T({ type: 'square', f0: 660, dur: 0.04, vol: 0.06 }); break;
      case 'ui_ok': T({ type: 'square', f0: 660, dur: 0.05, vol: 0.09 }); T({ type: 'square', f0: 990, dur: 0.09, vol: 0.09, t: this.ctx.currentTime + 0.05 }); break;
      case 'ui_back': T({ type: 'square', f0: 500, f1: 300, dur: 0.1, vol: 0.08 }); break;
      case 'error': T({ type: 'square', f0: 180, dur: 0.12, vol: 0.12 }); T({ type: 'square', f0: 140, dur: 0.15, vol: 0.12, t: this.ctx.currentTime + 0.1 }); break;
      case 'talk': T({ type: 'square', f0: 420 + Math.random() * 120, dur: 0.03, vol: 0.04 }); break;
      case 'door': N({ dur: 0.2, vol: 0.15, lp: 1200 }); T({ type: 'triangle', f0: 200, f1: 120, dur: 0.2, vol: 0.12 }); break;
      case 'roar': T({ type: 'sawtooth', f0: 110, f1: 55, dur: 0.9, vol: 0.28, lp: 900 }); N({ dur: 0.8, vol: 0.22, lp: 800, f1: 200 }); break;
      case 'die': T({ type: 'square', f0: 400, f1: 60, dur: 0.35, vol: 0.14 }); N({ dur: 0.25, vol: 0.18, lp: 2500, f1: 200 }); break;
      case 'save': [659, 784, 988, 1319].forEach((f, i) => T({ type: 'sine', f0: f, dur: 0.5, vol: 0.14, t: this.ctx!.currentTime + i * 0.1 })); break;
      case 'telegraph': T({ type: 'square', f0: 900, dur: 0.05, vol: 0.06 }); T({ type: 'square', f0: 1200, dur: 0.06, vol: 0.06, t: this.ctx.currentTime + 0.06 }); break;
      case 'spirit': T({ type: 'sine', f0: 500, f1: 1000, dur: 0.4, vol: 0.14 }); T({ type: 'triangle', f0: 750, f1: 1500, dur: 0.4, vol: 0.08 }); break;
      case 'meteor': T({ type: 'sawtooth', f0: 900, f1: 90, dur: 0.6, vol: 0.12 }); break;
    }
  }

  // ---------- Music ----------
  music(name: string) {
    if (name === this.current) return;
    this.current = name;
    if (!this.ctx) return;
    if (this.timer !== null) {
      clearInterval(this.timer);
      this.timer = null;
    }
    if (!name || !THEMES[name]) return;
    this.step = 0;
    this.nextTime = this.ctx.currentTime + 0.15;
    this.timer = window.setInterval(() => this.schedule(), 80);
  }

  private schedule() {
    const c = this.ctx!;
    const th = THEMES[this.current];
    if (!th) return;
    const stepDur = 60 / th.bpm / 4;
    while (this.nextTime < c.currentTime + 0.4) {
      this.playStep(th, this.step, this.nextTime, stepDur);
      this.nextTime += stepDur;
      this.step++;
    }
  }

  private degree(th: Theme, d: number, oct = 0): number {
    const n = th.scale.length;
    const o = Math.floor(d / n);
    const i = ((d % n) + n) % n;
    return th.root + th.scale[i] + 12 * (o + oct);
  }

  private playStep(th: Theme, step: number, t: number, sd: number) {
    const bar = Math.floor(step / 16);
    const s16 = step % 16;
    const chord = th.prog[bar % th.prog.length];
    const dest = this.musicGain;
    const rng = new Rng(th.seed * 997 + (bar % 8) * 131 + s16 * 7);
    // bass on beats
    if (s16 % 4 === 0 || (th.drums === 2 && s16 % 2 === 0)) {
      const note = this.degree(th, chord, -2);
      this.tone({ type: 'triangle', f0: mtof(note), dur: sd * (th.drums === 2 ? 1.8 : 3.5), vol: 0.34, t, dest, lp: 700 });
    }
    // arpeggio
    if (th.arp && s16 % 2 === 0) {
      const tones = [0, 2, 4, 2];
      const note = this.degree(th, chord + tones[(s16 / 2) % 4], 0);
      this.tone({ type: 'square', f0: mtof(note), dur: sd * 1.6, vol: 0.05, t, dest, lp: 2200 });
    }
    // pad on bar start
    if (s16 === 0) {
      for (const k of [0, 2, 4]) {
        this.tone({ type: 'sine', f0: mtof(this.degree(th, chord + k, 0)), dur: sd * 15, vol: 0.06, t, dest, attack: 0.3 });
      }
    }
    // melody (phrase repeats every 8 bars; second half answers the first)
    const phraseStep = s16 % 2 === 0 || rng.chance(0.25);
    if (phraseStep && rng.chance(th.density) && (bar % 4 !== 3 || s16 < 10)) {
      const pr = new Rng(th.seed * 31 + (bar % 8) * 17);
      let d = chord + 4 + pr.int(-1, 3);
      for (let i = 0; i < s16; i++) d += pr.int(-2, 2) * (i % 3 === 0 ? 1 : 0);
      const note = this.degree(th, d, 1);
      const len = rng.pick([1, 2, 2, 3, 4]);
      this.tone({ type: th.lead, f0: mtof(note), dur: sd * len * 0.95, vol: th.leadVol, t, dest, attack: 0.01, lp: 3500 });
    }
    // drums
    if (th.drums) {
      const d = th.drums;
      if (s16 % 8 === 0 || (d === 2 && (s16 === 6 || s16 === 14 || s16 === 10))) {
        this.tone({ type: 'sine', f0: 150, f1: 40, dur: 0.15, vol: 0.4, t, dest });
      }
      if (s16 % 8 === 4) {
        this.noise({ dur: 0.12, vol: 0.2, t, dest, hp: 1500 });
        this.tone({ type: 'triangle', f0: 220, f1: 110, dur: 0.08, vol: 0.12, t, dest });
      }
      if (s16 % 2 === 0 && (d === 2 || s16 % 4 === 2)) this.noise({ dur: 0.04, vol: 0.06, t, dest, hp: 6000 });
    }
  }

  stopMusic() {
    this.current = '';
    if (this.timer !== null) clearInterval(this.timer);
    this.timer = null;
  }
}

export const Audio = new AudioEngine();
