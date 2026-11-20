(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var en = document.documentElement.lang === 'en' || new URLSearchParams(location.search).get('lang') === 'en';
  var T = function (de, eng) { return en ? eng : de; };

  if (en) {
    document.documentElement.lang = 'en';
    document.title = 'Smart TV Edition · Money Compass Pro';
    var sw = document.querySelector('.langsw');
    if (sw) { sw.href = '?lang=de'; sw.hreflang = 'de'; sw.textContent = 'Deutsch'; }
    $('tvTag').textContent = 'Exclusive to Money Compass Plus';
    $('tvH1').textContent = 'Your financial cockpit in 1080p on your Smart TV.';
    $('tvLead').textContent = 'View freedom days, compass dial, portfolio mix, compound curve and wealth audit sharp from your couch — controlled by TV remote, completely local on your home network.';
    $('tvFeatsTitle').textContent = '4 graphic cockpits built for the big screen';
    $('f1t').textContent = '1. Compass & Path';
    $('f1d').textContent = 'Golden compass dial with rotating freedom needle plus 20-year wealth trajectory to break-even.';
    $('f2t').textContent = '2. Portfolio & Mix';
    $('f2d').textContent = 'Asset-class donut chart, 5–15% gold target corridor and live holding bars.';
    $('f3t').textContent = '3. Compound & Income';
    $('f3d').textContent = 'Dual-area chart comparing contributions, compound gains and inflation-adjusted purchasing power.';
    $('f4t').textContent = '4. Audit & Stress Test';
    $('f4d').textContent = '5-axis wealth audit radar chart (0–100 score) plus crash shock & emergency cash fortress.';
    $('tvHowTitle').textContent = 'Runs on any Smart TV';
    $('tvHowDesc').innerHTML = 'After downloading, unzip the package, launch <b>TV-Start-Mac.command</b> or <code>python3 TV-Start.py</code> and open the shown URL in your Smart TV browser (VIDAA, Samsung, LG, Google TV, Fire TV). Use <b>Backup (.json)</b> to load your saved numbers from the web app — everything stays strictly local.';
  }

  var cfg = window.GK_ACCOUNT_CONFIG || {};
  var B = window.GK_BILLING || {};
  var gate = $('tvGate'), title = $('tvGateTitle'), desc = $('tvGateDesc'), acts = $('tvActions'), msg = $('tvMsg');

  function showMsg(txt) {
    msg.hidden = !txt;
    msg.textContent = txt || '';
  }

  function renderGuest(note) {
    gate.classList.remove('ok');
    title.textContent = T('Smart-TV-Edition nur ab Geld-Kompass Plus', 'Smart TV Edition requires Money Compass Plus');
    desc.textContent = note || T(
      'Melde dich mit deinem kostenlosen Konto an. Sobald Geld-Kompass Plus aktiv ist, wird der Download direkt hier freigeschaltet.',
      'Sign in with your free account. Once Money Compass Plus is active, the download unlocks right here.'
    );
    acts.innerHTML =
      '<a class="btn pri" id="tvLoginBtn" href="/konto/?lang=' + (en ? 'en' : 'de') + '&next=tv">' + T('Mit Konto anmelden', 'Sign in with account') + '</a>' +
      '<a class="btn" id="tvPlusBtn" href="/app/?lang=' + (en ? 'en' : 'de') + '#plus">' + T('Plus entdecken', 'Discover Plus') + '</a>';
  }

  function renderNoPlus(email) {
    gate.classList.remove('ok');
    title.textContent = T('Plus erforderlich für den Download', 'Plus required to download');
    desc.textContent = T(
      'Angemeldet als ' + email + '. Für die Smart-TV-Edition wird ein aktives Geld-Kompass Plus benötigt.',
      'Signed in as ' + email + '. An active Money Compass Plus pass or subscription is required for the Smart TV Edition.'
    );
    acts.innerHTML =
      '<a class="btn pri" id="tvPlusBtn" href="/app/?lang=' + (en ? 'en' : 'de') + '#plus">' + T('Geld-Kompass Plus freischalten', 'Unlock Money Compass Plus') + '</a>' +
      '<a class="btn" href="/konto/?lang=' + (en ? 'en' : 'de') + '&next=tv">' + T('Konto wechseln', 'Switch account') + '</a>';
  }

  function triggerDownload(token, btn) {
    var fnBase = (B.functions || (cfg.url + '/functions/v1/'));
    btn.disabled = true;
    var oldTxt = btn.textContent;
    btn.textContent = T('Paket wird geladen …', 'Downloading package …');
    showMsg('');
    fetch(fnBase + 'tv-download', {
      headers: { Authorization: 'Bearer ' + token, apikey: cfg.key || B.apikey || '' }
    }).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.blob();
    }).then(function (blob) {
      var u = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = u;
      a.download = 'Geld-Kompass-Pro-TV.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(function () { URL.revokeObjectURL(u); }, 4000);
      btn.disabled = false;
      btn.textContent = oldTxt;
      showMsg(T('Download gestartet: Geld-Kompass-Pro-TV.zip', 'Download started: Geld-Kompass-Pro-TV.zip'));
    }).catch(function () {
      btn.disabled = false;
      btn.textContent = oldTxt;
      showMsg(T('Download konnte nicht geladen werden. Bitte prüfe deine Plus-Mitgliedschaft und versuche es erneut.', 'Download failed. Please verify your Plus status and try again.'));
    });
  }

  function renderUnlocked(email, token, info) {
    gate.classList.add('ok');
    title.textContent = T('Smart-TV-Edition freigeschaltet', 'Smart TV Edition unlocked');
    var kb = info && info.sizeBytes ? Math.max(1, Math.round(info.sizeBytes / 1024)) + ' KB' : '';
    desc.textContent = T(
      'Plus aktiv für ' + email + '. Version ' + ((info && info.version) || '1.0.0') + (kb ? ' (' + kb + ')' : '') + ' steht bereit.',
      'Plus active for ' + email + '. Version ' + ((info && info.version) || '1.0.0') + (kb ? ' (' + kb + ')' : '') + ' is ready.'
    );
    acts.innerHTML = '<button class="btn pri" type="button" id="tvDownloadBtn">' + T('Geld-Kompass-Pro-TV.zip herunterladen', 'Download Geld-Kompass-Pro-TV.zip') + '</button>' +
      '<a class="btn" href="/app/?lang=' + (en ? 'en' : 'de') + '#data">' + T('Backup (.json) exportieren', 'Export backup (.json)') + '</a>';
    $('tvDownloadBtn').addEventListener('click', function () { triggerDownload(token, this); });
  }

  if (!cfg.url || !cfg.key || !window.supabase) {
    renderGuest();
    return;
  }

  var client = window.supabase.createClient(cfg.url, cfg.key, {
    auth: { storageKey: 'gk.account.v1', persistSession: true, autoRefreshToken: true, detectSessionInUrl: false }
  });

  Promise.all([client.auth.getSession(), client.auth.getUser()]).then(function (res) {
    var sess = res[0] && res[0].data && res[0].data.session;
    var uRes = res[1] && res[1].data && res[1].data.user;
    if (!sess || !sess.access_token || !uRes || uRes.is_anonymous || !uRes.email_confirmed_at) {
      renderGuest();
      return;
    }
    var m = uRes.app_metadata || {};
    var isPlus = m.gk_admin === true || !!(m.gk_plus && m.gk_plus.active === true && Number(m.gk_plus.until) > Date.now());
    if (!isPlus) {
      renderNoPlus(uRes.email || '');
      return;
    }
    var fnBase = (B.functions || (cfg.url + '/functions/v1/'));
    fetch(fnBase + 'tv-download?info=1', {
      headers: { Authorization: 'Bearer ' + sess.access_token, apikey: cfg.key || B.apikey || '' }
    }).then(function (r) {
      if (r.status === 403 || r.status === 401) {
        renderNoPlus(uRes.email || '');
        return null;
      }
      return r.json().catch(function () { return {}; });
    }).then(function (info) {
      if (!info) return;
      renderUnlocked(uRes.email || '', sess.access_token, info);
    }).catch(function () {
      renderUnlocked(uRes.email || '', sess.access_token, null);
    });
  }).catch(function () {
    renderGuest();
  });
})();
