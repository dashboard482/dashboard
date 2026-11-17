/* Adaptación a Telegram Mini Apps. Se incluye con: <script src="telegram.js" defer></script>
   Fuera de Telegram no hace nada. */
(function () {
  'use strict';
  if (window.top !== window) return; // no actuar dentro de iframes (p. ej. el indicador oculto del hub)

  var MAP = { noticias: 'noticias.html', btc: 'caro_barato_btc.html', donar: 'donaciones.html', guerra: 'guerra_liquidez.html', dominancia: 'dominancia.html', ciclo: 'ciclo.html', halving: 'halvingbtc.html', compresion: 'compresion.html', trivia: 'trivia.html', ticker: 'ticker.html', alerta: 'alerta_btc.html', street: 'street_rush_3d.html', panel: 'btc_panel.html', coste: 'coste_btc.html', directo: 'noticias_directo.html', tv: 'tv_directo.html' };
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
