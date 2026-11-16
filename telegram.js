/* Adaptación a Telegram Mini Apps. Se incluye con: <script src="telegram.js" defer></script>
   Fuera de Telegram no hace nada. */
(function () {
  'use strict';
  if (window.top !== window) return; // no actuar dentro de iframes (p. ej. el indicador oculto del hub)

  var MAP = { noticias: 'noticias.html', btc: 'caro_barato_btc.html', donar: 'donaciones.html', guerra: 'guerra_liquidez.html', dominancia: 'dominancia.html', ciclo: 'ciclo.html', halving: 'halvingbtc.html', compresion: 'compresion.html', trivia: 'trivia.html', ticker: 'ticker.html', alerta: 'alerta_btc.html', street: 'street_rush_3d.html', panel: 'btc_panel.html', coste: 'coste_btc.html' };
  var hub = new URL('index.html', location.href).href;
  var isHub = /\/(index\.html)?$/.test(location.pathname);

  if (window.Telegram && window.Telegram.WebApp) init();
  else {
    var s = document.createElement('script');
    s.src = 'https://telegram.org/js/telegram-web-app.js';
    s.onload = init;
    document.head.appendChild(s);
  }

  function init() {
    var tg = window.Telegram && window.Telegram.WebApp;
    if (!tg || !tg.initData) return; // no estamos dentro de Telegram

    try { tg.ready(); tg.expand(); } catch (e) {}

    // pantalla completa de Telegram: dejar sitio arriba para la hora/batería y los botones de Telegram
    function margenSuperior() {
      try {
        var t = ((tg.safeAreaInset && tg.safeAreaInset.top) || 0) + ((tg.contentSafeAreaInset && tg.contentSafeAreaInset.top) || 0);
        if (tg.isFullscreen && t < 60) t = 100;
        document.documentElement.style.setProperty('--tgtop', t + 'px');
      } catch (e) {}
    }
    margenSuperior();
    try { ['safeAreaChanged', 'contentSafeAreaChanged', 'fullscreenChanged', 'viewportChanged'].forEach(function (ev) { tg.onEvent(ev, margenSuperior); }); } catch (e) {}

    // barra de Telegram a juego con el fondo de la página
    try {
      var c = (getComputedStyle(document.documentElement).getPropertyValue('--bg') || '').trim();
      var col = /^#[0-9a-f]{6}$/i.test(c) ? c : '#0e1117';
      tg.setHeaderColor(col); tg.setBackgroundColor(col);
      if (tg.setBottomBarColor) tg.setBottomBarColor(col);
    } catch (e) {}

    // en las páginas con gráficos, evitar que un gesto hacia abajo cierre la app
    if (!isHub && tg.disableVerticalSwipes) { try { tg.disableVerticalSwipes(); } catch (e) {} }

    // botón atrás de Telegram: oculto en el hub, vuelve al hub en el resto
    try {
      if (isHub) tg.BackButton.hide();
      else { tg.BackButton.show(); tg.BackButton.onClick(function () { location.href = hub; }); }
    } catch (e) {}

    // enlaces: las páginas propias se abren dentro; las externas con el navegador de Telegram
    document.addEventListener('click', function (e) {
      if (e.target.closest && e.target.closest('button')) return;
      var a = e.target.closest && e.target.closest('a[href]');
      if (!a) return;
      var u; try { u = new URL(a.href, location.href); } catch (_) { return; }
      if (!/^https?:$/.test(u.protocol)) return;
      e.preventDefault();
      if (u.origin === location.origin) location.href = u.href;
      else if (u.hostname === 't.me') tg.openTelegramLink(u.href);
      else tg.openLink(u.href);
    }, true);

    // enlaces profundos: t.me/anafra_bot/hubfinanciero?startapp=noticias
    var sp = (tg.initDataUnsafe && tg.initDataUnsafe.start_param) || '';
    try {
      if (isHub && MAP[sp] && !sessionStorage.getItem('tgrouted')) {
        sessionStorage.setItem('tgrouted', '1');
        location.replace(new URL(MAP[sp], location.href).href);
      }
    } catch (e) {}
  }
})();
