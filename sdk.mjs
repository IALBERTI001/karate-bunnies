// CrazyGames SDK wrapper. Every SDK call goes through here, and everything works with no SDK at all
// (GitHub Pages, local play, an ad blocker): calls become no-ops and saves use localStorage.
// On crazygames.com (or ?useLocalSdk=true) the v3 SDK is loaded, gameplay/loading events are reported and saves go
// through the Data module, which mirrors localStorage for guests and syncs to the player's account.
const SDK_URL = 'https://sdk.crazygames.com/crazygames-sdk-v3.js';
const params = (() => { try { return new URLSearchParams(location.search); } catch { return new URLSearchParams(); } })();
const onPortal = () => { try { return /(^|\.)crazygames\.[a-z.]+$/.test(location.hostname) || params.get('useLocalSdk') === 'true'; } catch { return false; } };

function loadScript(timeoutMs) {
  return new Promise(resolve => {
    if (window.CrazyGames?.SDK) return resolve(true);
    if (!onPortal()) return resolve(false);
    const s = document.createElement('script'); s.src = SDK_URL; s.async = true;
    const t = setTimeout(() => resolve(!!window.CrazyGames?.SDK), timeoutMs);
    s.onload = () => { clearTimeout(t); resolve(true); }; s.onerror = () => { clearTimeout(t); resolve(false); };
    document.head.append(s);
  });
}

let sdk = null, playing = false, mutedBySdk = false;
const muteListeners = new Set();
const call = fn => { try { return fn(); } catch { return undefined; } };

export const GameSDK = {
  /** 'crazygames' | 'local' | 'disabled' | 'none' */
  env: 'none',
  async init(timeoutMs = 4000) {
    const loaded = await loadScript(timeoutMs);
    const candidate = loaded ? window.CrazyGames?.SDK : null;
    if (!candidate) return this;
    try {
      await Promise.race([candidate.init(), new Promise((_, no) => setTimeout(() => no(new Error('SDK init timeout')), timeoutMs))]);
      this.env = candidate.environment || 'crazygames';
      if (this.env === 'disabled') return this;
      sdk = candidate;
      call(() => sdk.game.loadingStart());
      mutedBySdk = !!call(() => sdk.game.settings?.muteAudio);
      call(() => sdk.game.addSettingsChangeListener(s => { mutedBySdk = !!s?.muteAudio; muteListeners.forEach(f => f(mutedBySdk)); }));
    } catch { sdk = null; }
    return this;
  },
  get active() { return !!sdk; },
  /** True where the platform provides its own fullscreen (no custom button allowed there). */
  get platformFullscreen() { return !!sdk || onPortal(); },
  loadingStop() { if (sdk) call(() => sdk.game.loadingStop()); },
  /** Report whether the player is actively playing; only changes are sent. */
  gameplay(on) {
    on = !!on; if (on === playing) return; playing = on;
    if (sdk) call(() => on ? sdk.game.gameplayStart() : sdk.game.gameplayStop());
  },
  happytime() { if (sdk) call(() => sdk.game.happytime()); },
  get muted() { return mutedBySdk; },
  onMute(fn) { muteListeners.add(fn); },
  /** localStorage-style save store: the Data module when available, otherwise localStorage. */
  data: {
    getItem(k) {
      const cloud = sdk ? call(() => sdk.data.getItem(k)) : undefined;
      if (cloud !== undefined && cloud !== null) return cloud;
      const local = call(() => localStorage.getItem(k)) ?? null;
      // Carry progress from before the Data module into it, so returning players keep it.
      if (sdk && local !== null) call(() => sdk.data.setItem(k, local));
      return local;
    },
    setItem(k, v) {
      let ok = false;
      if (sdk) { call(() => sdk.data.setItem(k, v)); ok = true; }
      try { localStorage.setItem(k, v); ok = true; } catch {}
      return ok;
    }
  }
};
