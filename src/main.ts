import '@fontsource/pixelify-sans/400.css';
import '@fontsource/pixelify-sans/700.css';
import { Disp } from './engine/display';
import { Input, setupTouchControls } from './engine/input';
import { Audio } from './engine/audio';
import { SceneMgr, TitleScene, GameScene, startNewGame } from './game/scenes';
import { G } from './game/state';
import { artPreview, artZoom, portraitPreview, worldPreview } from './dev/artpreview';

async function boot() {
  const q = new URLSearchParams(location.search);
  if (q.has('artpreview')) return artPreview();
  if (q.has('zoom')) return artZoom(q.get('zoom')!.split(','), 9);
  if (q.has('portraits')) return portraitPreview();
  if (q.has('worldprev')) return worldPreview();

  const app = document.getElementById('app')!;
  Disp.init(app);
  Input.init();
  setupTouchControls(app);
  Input.onFirstGesture.push(() => Audio.unlock());
  try {
    await Promise.all([document.fonts.load('8px "Pixelify Sans"'), document.fonts.load('700 8px "Pixelify Sans"')]);
  } catch { /* fall back to monospace */ }

  const title = new TitleScene();
  SceneMgr.go(title);

  // debug helpers (used by automated tests): ?debug=map,tx,ty
  const dbg = q.get('debug');
  if (dbg) {
    const [map, tx, ty, lv] = dbg.split(',');
    startNewGame('Kai', (q.get('hero') as 'kai' | 'aiko') ?? 'kai');
    Object.assign(G.flags, { intro_done: true, tutorial_done: true, battle1_done: true, mira_briefed: true, arrived_village: true });
    G.map = map; G.px = parseInt(tx) * 16 + 8; G.py = parseInt(ty) * 16 + 12;
    if (lv) { G.level = parseInt(lv); G.sp = parseInt(lv); const st = G.stats(); G.hp = st.maxHp; G.mp = st.maxMp; }
    G.quests['m1_call'] = { state: 'done', step: 3, progress: 0 };
    for (const f of (q.get('flags') ?? '').split(',').filter(Boolean)) G.flags[f] = true;
    if (q.has('lyra')) G.flags['ally_lyra'] = true;
    SceneMgr.go(new GameScene('load'));
  }

  let last = performance.now();
  const frame = (now: number) => {
    const dt = Math.max(0, Math.min(0.1, (now - last) / 1000));
    last = now;
    Input.poll(dt);
    const sc = SceneMgr.current!;
    sc.update(dt);
    Disp.beginFrame();
    sc.draw(Disp.g);
    Disp.blitWorld();
    Disp.beginUI();
    sc.drawUI(Disp.ui);
    Disp.endUI();
    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
}
void boot();
