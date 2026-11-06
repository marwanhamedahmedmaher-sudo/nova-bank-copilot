/* Telos Comment Widget — Giscus per recommendation.
 *
 * Comments live in GitHub Discussions (one thread per recommendation) via Giscus,
 * an open-source widget. No tokens, API keys, or backend. Each viewer authenticates
 * with their own GitHub account. The repo/category IDs below are PUBLIC identifiers,
 * not secrets — the registry substitutes them at publish time from ~/.telos/config.json.
 */

var GISCUS_CONFIG = {
  repo: '',
  repoId: '',
  category: '',
  categoryId: ''
};

var _activePanel = null;
var _activeRec = null;

function _giscusConfigured() {
  // Comments are "off" when the registry left the placeholders unsubstituted
  // (still carry the __TELOS_ sentinel) OR substituted them with empty strings
  // (no `comments` block in config). Either way, show the disabled state with a
  // reason instead of loading a broken Giscus iframe.
  return [GISCUS_CONFIG.repo, GISCUS_CONFIG.repoId, GISCUS_CONFIG.categoryId]
    .every(function (v) { return v && v.indexOf('__TELOS_') === -1; });
}

function initComments(pagePath) {
  var configured = _giscusConfigured();

  if (configured) {
    // Giscus emits the discussion's comment count via postMessage when a panel
    // loads. Use it to label the toggle of whichever rec is currently open.
    window.addEventListener('message', function (event) {
      if (event.origin !== 'https://giscus.app') return;
      var data = event.data;
      if (typeof data !== 'object' || !data.giscus) return;
      var meta = data.giscus;
      if (meta.discussion && _activeRec) {
        var count = meta.discussion.totalCommentCount || 0;
        _updateToggleCount(_activeRec, count);
      }
    });
  }

  document.querySelectorAll('.telos-comments').forEach(function (el) {
    var rec = el.dataset.rec;
    if (configured) {
      _renderRecToggle(el, rec, pagePath);
    } else {
      _renderDisabled(el);
    }
  });
}

function _renderDisabled(container) {
  container.innerHTML = '';
  var note = document.createElement('button');
  note.className = 'tc-toggle tc-disabled';
  note.disabled = true;
  note.title = 'Run /telos-setup in connected mode and link a GitHub repo to enable comments.';
  note.innerHTML = '<span class="tc-plus">+</span> Comment <span class="tc-off">(connect a repo to enable)</span>';
  container.appendChild(note);
}

function _updateToggleCount(rec, count) {
  var el = document.querySelector('.telos-comments[data-rec="' + rec + '"]');
  if (!el) return;
  var btn = el.querySelector('.tc-toggle');
  if (!btn) return;
  btn.setAttribute('data-count', count);
  _setToggleText(btn, count, btn.classList.contains('expanded'));
}

function _setToggleText(btn, count, isOpen) {
  var arrow = isOpen ? '▴' : '▾';
  if (count > 0) {
    btn.innerHTML = '💬 ' + count + ' comment' + (count !== 1 ? 's' : '') +
      ' <span class="tc-arrow">' + arrow + '</span>';
    btn.classList.add('has-comments');
  } else {
    if (isOpen) {
      btn.innerHTML = '💬 Comment <span class="tc-arrow">' + arrow + '</span>';
    } else {
      btn.innerHTML = '<span class="tc-plus">+</span> Comment <span class="tc-arrow">' +
        arrow + '</span>';
    }
    btn.classList.remove('has-comments');
  }
}

function _renderRecToggle(container, rec, pagePath) {
  container.innerHTML = '';

  var btn = document.createElement('button');
  btn.className = 'tc-toggle';
  btn.setAttribute('data-count', '0');
  _setToggleText(btn, 0, false);

  var panel = document.createElement('div');
  panel.className = 'tc-panel';

  btn.onclick = function () {
    var isOpen = panel.classList.contains('open');

    if (isOpen) {
      _closePanel(panel, btn);
      return;
    }

    // Only one Giscus iframe loaded at a time — close any other open panel first.
    if (_activePanel && _activePanel !== panel) {
      var prevBtn = _activePanel.parentElement.querySelector('.tc-toggle');
      _closePanel(_activePanel, prevBtn);
    }

    panel.classList.add('open');
    btn.classList.add('expanded');
    _setToggleText(btn, parseInt(btn.getAttribute('data-count') || '0'), true);
    _activePanel = panel;
    _activeRec = rec;

    _loadGiscus(panel, pagePath + '/rec-' + rec);
  };

  container.appendChild(btn);
  container.appendChild(panel);
}

function _closePanel(panel, btn) {
  panel.classList.remove('open');
  panel.innerHTML = '';
  if (btn) {
    btn.classList.remove('expanded');
    _setToggleText(btn, parseInt(btn.getAttribute('data-count') || '0'), false);
  }
  if (_activePanel === panel) {
    _activePanel = null;
    _activeRec = null;
  }
}

function _loadGiscus(container, term) {
  container.innerHTML = '';

  var script = document.createElement('script');
  script.src = 'https://giscus.app/client.js';
  script.setAttribute('data-repo', GISCUS_CONFIG.repo);
  script.setAttribute('data-repo-id', GISCUS_CONFIG.repoId);
  script.setAttribute('data-category', GISCUS_CONFIG.category);
  script.setAttribute('data-category-id', GISCUS_CONFIG.categoryId);
  script.setAttribute('data-mapping', 'specific');
  script.setAttribute('data-term', term);
  script.setAttribute('data-strict', '0');
  script.setAttribute('data-reactions-enabled', '0');
  script.setAttribute('data-emit-metadata', '1');
  script.setAttribute('data-input-position', 'bottom');
  script.setAttribute('data-theme', 'preferred_color_scheme');
  script.setAttribute('data-lang', 'en');
  script.setAttribute('data-loading', 'lazy');
  script.crossOrigin = 'anonymous';
  script.async = true;
  container.appendChild(script);
}
