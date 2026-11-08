/**
 * THÚ Y TÙNG & THẢO — APPLICATION LOGIC
 * Luxury Dark Glassmorphism (@_code_and_chill_ Theme)
 * 100% Real Data & Zero Hallucination
 */

let state = {
  inventory: [],
  patients: [],
  sales: [],
  stats: null,
  currentView: 'dashboard',
  chartInstance: null,
  chartPeriod: 'month',
};

// ── Admin Authentication Logic ──
function checkAuth() {
  const token = localStorage.getItem('tytt_admin_token');
  const overlay = document.getElementById('adminLoginOverlay');
  if (!overlay) return true;

  if (token) {
    overlay.classList.add('auth-hidden');
    return true;
  } else {
    overlay.classList.remove('auth-hidden');
    const pwdInput = document.getElementById('adminPasswordInput');
    if (pwdInput) {
      setTimeout(() => pwdInput.focus(), 150);
    }
    return false;
  }
}

async function handleAdminLogin(event) {
  if (event) event.preventDefault();

  const pwdInput = document.getElementById('adminPasswordInput');
  const submitBtn = document.getElementById('adminLoginSubmitBtn');
  const errBox = document.getElementById('adminLoginError');
  const errText = document.getElementById('adminLoginErrorText');
  const inputWrap = document.getElementById('adminPasswordInputWrap');

  const password = pwdInput ? pwdInput.value.trim() : '';
  if (!password) {
    if (errBox) {
      errBox.classList.remove('hidden');
      errText.textContent = 'Vui lòng nhập mật khẩu quản trị.';
    }
    return;
  }

  // Loading state
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Đang xác thực...</span>';
    if (window.lucide) lucide.createIcons();
  }
  if (errBox) errBox.classList.add('hidden');

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password })
    });

    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('tytt_admin_token', data.token || 'admin_session_valid');

      const overlay = document.getElementById('adminLoginOverlay');
      if (overlay) overlay.classList.add('auth-hidden');

      showToast('Đăng nhập Quản trị thành công! Chào mừng Bác sĩ Tùng & Thảo.');

      // Load all dashboard components
      await loadHealth();
      await loadStats();
      await loadInventory();
      await loadPatients();
      await loadSales();
    } else {
      let msg = 'Mật khẩu quản trị không chính xác. Vui lòng thử lại.';
      try {
        const errData = await res.json();
        if (errData && errData.detail) msg = errData.detail;
      } catch (_) {}

      if (errBox) {
        errBox.classList.remove('hidden');
        if (errText) errText.textContent = msg;
      }
      if (inputWrap) {
        inputWrap.classList.remove('input-shake');
        void inputWrap.offsetWidth; // trigger reflow
        inputWrap.classList.add('input-shake');
      }
      if (pwdInput) {
        pwdInput.value = '';
        pwdInput.focus();
      }
    }
  } catch (err) {
    if (errBox) {
      errBox.classList.remove('hidden');
      if (errText) errText.textContent = 'Lỗi kết nối máy chủ: ' + err.message;
    }
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i data-lucide="log-in" class="w-4 h-4"></i><span>Đăng Nhập Quản Trị</span>';
      if (window.lucide) lucide.createIcons();
    }
  }
}

function handleAdminLogout() {
  if (confirm('Bạn có chắc chắn muốn đăng xuất khỏi quyền Quản trị?')) {
    localStorage.removeItem('tytt_admin_token');
    const overlay = document.getElementById('adminLoginOverlay');
    if (overlay) {
      overlay.classList.remove('auth-hidden');
      const pwdInput = document.getElementById('adminPasswordInput');
      if (pwdInput) {
        pwdInput.value = '';
        setTimeout(() => pwdInput.focus(), 150);
      }
    }
    showToast('Đã đăng xuất tài khoản quản trị an toàn.');
  }
}

function togglePasswordVisibility(inputId, iconId) {
  const input = document.getElementById(inputId);
  const icon = document.getElementById(iconId);
  if (!input) return;

  if (input.type === 'password') {
    input.type = 'text';
    if (icon) icon.setAttribute('data-lucide', 'eye-off');
  } else {
    input.type = 'password';
    if (icon) icon.setAttribute('data-lucide', 'eye');
  }
  if (window.lucide) lucide.createIcons();
}

window.checkAuth = checkAuth;
window.handleAdminLogin = handleAdminLogin;
window.handleAdminLogout = handleAdminLogout;
window.togglePasswordVisibility = togglePasswordVisibility;

// ── Initialization ──
document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  updateLiveDate();
  setupGlobalSearch();
  setupKeyboardShortcuts();

  const isAuthed = checkAuth();
  if (isAuthed) {
    await loadHealth();
    await loadStats();
    await loadInventory();
    await loadPatients();
    await loadSales();
  }

  // Set default sale date in modal to today
  const saleDateInput = document.getElementById('sale_date');
  if (saleDateInput) {
    saleDateInput.value = new Date().toISOString().slice(0, 10);
  }
});

// Update Header Date & Time (Real local Vietnamese date)
function updateLiveDate() {
  const now = new Date();
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const dateStr = now.toLocaleDateString('vi-VN', options);
  const el = document.getElementById('liveDateDisplay');
  if (el) {
    el.innerHTML = `<span>${dateStr}</span> <span class="text-slate-600">·</span> <span class="text-teal-400 font-semibold">Trung tâm điều hành</span>`;
  }
}

// ── Navigation View Switching ──
function switchView(viewName) {
  state.currentView = viewName;

  // List of all active views (no customer portal)
  const views = ['dashboard', 'inventory', 'patients', 'sales', 'rag', 'shopee', 'knowledge', 'settings'];
  views.forEach(v => {
    const el = document.getElementById(`view-${v}`);
    if (el) el.classList.add('hidden');
    const navBtn = document.getElementById(`nav-${v}`);
    if (navBtn) navBtn.classList.remove('active');
  });

  // Show target section
  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) targetView.classList.remove('hidden');

  const activeNav = document.getElementById(`nav-${viewName}`);
  if (activeNav) activeNav.classList.add('active');

  if (viewName === 'inventory') {
    renderInventoryTable();
  } else if (viewName === 'patients') {
    renderPatientsGrid();
  } else if (viewName === 'sales') {
    renderSalesTable();
  }

  if (window.lucide) lucide.createIcons();
}

// ── Real Backend API Calls ──

async function loadHealth() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    const pill = document.getElementById('supabaseStatusPill');
    if (pill) {
      if (data.supabase && data.supabase.connected) {
        pill.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span><span>Supabase (${data.supabase.latency_ms}ms)</span>`;
      } else {
        pill.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400"></span><span>Supabase Offline</span>`;
      }
    }
    const settingEl = document.getElementById('settingSupabaseStatus');
    if (settingEl) {
      settingEl.textContent = data.supabase.connected ? `Ổn định (${data.supabase.total_items} sản phẩm)` : 'Mất kết nối';
    }

    if (data.ai) {
      updateModelDisplayUI(data.ai.model, data.ai.reasoning_effort);
    }
  } catch (err) {
    console.error('Health check failed:', err);
  }
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    state.stats = data;

    // 1. Stat Cards (Honest Real Data)
    const todayEl = document.getElementById('dash-today-rev');
    const todaySubEl = document.getElementById('dash-today-sub');
    if (todayEl) {
      todayEl.textContent = (data.today_revenue || 0).toLocaleString('vi-VN') + ' đ';
    }
    if (todaySubEl) {
      if (data.today_revenue > 0) {
        todaySubEl.innerHTML = `<span class="text-emerald-400 font-semibold">✓ Đã ghi nhận hôm nay</span>`;
      } else {
        todaySubEl.innerHTML = `<span>Chưa có giao dịch</span><button onclick="openAddSaleModal()" class="text-teal-400 hover:underline text-[10.5px]">+ Nhập</button>`;
      }
    }

    const weekEl = document.getElementById('dash-week-rev');
    const weekSubEl = document.getElementById('dash-week-sub');
    if (weekEl) {
      weekEl.textContent = (data.week_revenue || 0).toLocaleString('vi-VN') + ' đ';
    }
    if (weekSubEl) {
      weekSubEl.textContent = data.week_revenue > 0 ? `Tổng 7 ngày gần nhất` : 'Chưa phát sinh';
    }

    const totalItemsEl = document.getElementById('dash-total-items');
    if (totalItemsEl) {
      totalItemsEl.innerHTML = `${data.total_quantity} <span class="text-xs text-slate-400 font-normal">đơn vị</span>`;
    }

    const totalSkusEl = document.getElementById('dash-total-skus');
    if (totalSkusEl) totalSkusEl.textContent = data.total_products;

    const lowStockEl = document.getElementById('dash-low-stock-count');
    const lowStockSubEl = document.getElementById('dash-low-stock-sub');
    if (lowStockEl) {
      if (data.low_stock_count > 0) {
        lowStockEl.textContent = `${data.low_stock_count} SP cần nhập`;
        lowStockEl.className = 'text-2xl font-extrabold text-rose-400 tracking-tight';
        if (lowStockSubEl) lowStockSubEl.innerHTML = `<span class="text-rose-400 font-semibold">Tồn kho ≤ 5 đơn vị</span>`;
      } else {
        lowStockEl.textContent = 'An toàn';
        lowStockEl.className = 'text-2xl font-extrabold text-emerald-400 tracking-tight';
        if (lowStockSubEl) lowStockSubEl.innerHTML = `<i data-lucide="shield-check" class="w-3.5 h-3.5 text-emerald-400"></i><span class="text-emerald-400">Tồn kho đạt chuẩn</span>`;
      }
    }

    // 2. Goal Stats
    const goalTitleEl = document.getElementById('goalTitleDisplay');
    const currentMonthName = new Date().toLocaleDateString('vi-VN', { month: 'long' });
    if (goalTitleEl) goalTitleEl.textContent = `Chỉ Tiêu ${currentMonthName.toUpperCase()}`;

    const goalPercent = data.goal_progress_percent || 0;
    const goalPercentEl = document.getElementById('goalPercentText');
    if (goalPercentEl) goalPercentEl.textContent = `${goalPercent}%`;

    const goalRecordedEl = document.getElementById('goalRecordedText');
    if (goalRecordedEl) goalRecordedEl.textContent = (data.monthly_goal_recorded || 0).toLocaleString('vi-VN') + ' đ';

    const goalTargetEl = document.getElementById('goalTargetDisplay');
    if (goalTargetEl) goalTargetEl.textContent = (data.monthly_goal_target || 50000000).toLocaleString('vi-VN') + ' đ';

    const goalStatusEl = document.getElementById('goalStatusHint');
    if (goalStatusEl) {
      goalStatusEl.textContent = goalPercent >= 100 ? '🎉 Đạt mục tiêu tháng' : (goalPercent > 0 ? `Tiến độ ${goalPercent}%` : 'Sẵn sàng ghi nhận');
    }

    // Circular SVG Progress Ring
    const circle = document.getElementById('goalProgressCircle');
    if (circle) {
      const circumference = 251.2;
      const offset = circumference - (goalPercent / 100) * circumference;
      circle.style.strokeDashoffset = offset;
    }

    const goalBar = document.getElementById('goalProgressBar');
    if (goalBar) {
      goalBar.style.width = `${goalPercent}%`;
    }

    // 3. System Connection & Real Stats
    const patientsStatEl = document.getElementById('dash-stat-patients');
    if (patientsStatEl) patientsStatEl.textContent = `${data.total_patients} ca điều trị`;

    const consultsStatEl = document.getElementById('dash-stat-consults');
    if (consultsStatEl) consultsStatEl.textContent = `${data.session_consultations} lượt hỏi`;

    const topItemEl = document.getElementById('dash-stat-top-item');
    if (topItemEl) topItemEl.textContent = data.top_inventory_product || 'Đang cập nhật';

    // 4. Sales Studio Chart or Empty State
    renderSalesChart(data.chart_points || []);

  } catch (err) {
    console.error('Stats loading failed:', err);
  }
}

async function loadInventory() {
  try {
    const res = await fetch('/api/inventory');
    state.inventory = await res.json();
    const badge = document.getElementById('badge-stock-count');
    if (badge) badge.textContent = state.inventory.length;
    renderInventoryTable();
  } catch (err) {
    console.error('Inventory loading failed:', err);
  }
}

async function loadPatients() {
  try {
    const res = await fetch('/api/patients');
    state.patients = await res.json();
    const badge = document.getElementById('badge-patients-count');
    if (badge) badge.textContent = state.patients.length;
    renderPatientsGrid();
  } catch (err) {
    console.error('Patients loading failed:', err);
  }
}

async function loadSales() {
  try {
    const res = await fetch('/api/sales');
    state.sales = await res.json();
    renderSalesTable();
  } catch (err) {
    console.error('Sales loading failed:', err);
  }
}

// ── Global Search Command Palette (Ctrl+K / ⌘K) & Smart Navigation ──
let searchDebounceTimer = null;

function setupGlobalSearch() {
  const input = document.getElementById('globalSearchInput');
  const resultsContainer = document.getElementById('globalSearchResults');
  if (!input || !resultsContainer) return;

  // Close search suggestions on clicking outside
  document.addEventListener('click', (e) => {
    if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
      resultsContainer.style.display = 'none';
      resultsContainer.classList.add('hidden');
    }
  });
}

window.handleSearchInput = function(e) {
  clearTimeout(searchDebounceTimer);
  const q = e.target.value.trim();
  const container = document.getElementById('globalSearchResults');
  if (!q) {
    if (container) {
      container.style.display = 'none';
      container.classList.add('hidden');
      container.innerHTML = '';
    }
    return;
  }

  searchDebounceTimer = setTimeout(async () => {
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      renderSearchResults(data, q);
    } catch (err) {
      console.error('Search failed:', err);
    }
  }, 150);
};

window.handleSearchKeyDown = function(e) {
  if (e.key === 'Enter') {
    e.preventDefault();
    const query = e.target.value.trim().toLowerCase();
    if (!query) return;

    // 1. Direct Module Navigation Matches
    if (query.includes('hồ sơ') || query.includes('bệnh án') || query.includes('benh an') || query.includes('ho so') || query.includes('ca bệnh')) {
      selectSearchResult('nav', 'patients');
      return;
    }
    if (query.includes('kho') || query.includes('thuốc') || query.includes('thuoc') || query.includes('dược') || query.includes('duoc') || query.includes('tồn kho')) {
      selectSearchResult('nav', 'inventory');
      return;
    }
    if (query.includes('doanh thu') || query.includes('tiền') || query.includes('sổ quỹ') || query.includes('so quy') || query.includes('bán hàng') || query.includes('hóa đơn')) {
      selectSearchResult('nav', 'sales');
      return;
    }
    if (query.includes('bác sĩ') || query.includes('phác đồ') || query.includes('bac si') || query.includes('phac do') || query.includes('rag') || query.includes('tư vấn') || query.includes('chẩn đoán')) {
      selectSearchResult('nav', 'rag');
      return;
    }
    if (query.includes('shopee') || query.includes('seo') || query.includes('bài đăng') || query.includes('bài viết')) {
      selectSearchResult('nav', 'shopee');
      return;
    }
    if (query.includes('cài đặt') || query.includes('cai dat') || query.includes('api') || query.includes('cấu hình')) {
      selectSearchResult('nav', 'settings');
      return;
    }
    if (query.includes('tri thức') || query.includes('tri thuc') || query.includes('tài liệu')) {
      selectSearchResult('nav', 'knowledge');
      return;
    }

    // 2. Click first suggestion from dropdown if rendered
    const firstOption = document.querySelector('#globalSearchResults [data-search-target]');
    if (firstOption) {
      firstOption.click();
      return;
    }

    // 3. Match Inventory item
    if (state.inventory && state.inventory.length > 0) {
      const match = state.inventory.find(i => (i.ten_sp || '').toLowerCase().includes(query) || (i.ma_sp || '').toLowerCase().includes(query));
      if (match) {
        selectSearchResult('inventory', match.ma_sp);
        return;
      }
    }

    // 4. Default: Query RAG Clinical AI
    selectSearchResult('rag', e.target.value);
  } else if (e.key === 'Escape') {
    closeSearchResults();
  }
};

function closeSearchResults() {
  const container = document.getElementById('globalSearchResults');
  if (container) {
    container.style.display = 'none';
    container.classList.add('hidden');
    container.innerHTML = '';
  }
  const input = document.getElementById('globalSearchInput');
  if (input) input.blur();
}

function setupKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      const input = document.getElementById('globalSearchInput');
      if (input) {
        input.focus();
        input.select();
      }
    } else if (e.key === 'Escape') {
      closeSearchResults();
      closeAddMedicineModal();
      closeAddPatientModal();
      closeAddSaleModal();
      closeEditGoalModal();
    }
  });
}

function renderSearchResults(data, query) {
  const container = document.getElementById('globalSearchResults');
  if (!container) return;

  const navCount = data.nav?.length || 0;
  const invCount = data.inventory?.length || 0;
  const patCount = data.patients?.length || 0;
  const kbCount = data.knowledge?.length || 0;
  const total = navCount + invCount + patCount + kbCount;

  if (total === 0) {
    container.innerHTML = `
      <div class="p-3 text-center text-slate-400">
        <div>Không tìm thấy dữ liệu khớp với "${query}"</div>
        <button onclick="selectSearchResult('rag', '${query.replace(/'/g, "\\'")}')" class="mt-2 text-teal-400 hover:underline text-[11px] font-semibold block mx-auto">
          Tra cứu Trợ lý Bác sĩ Ảo (RAG) ↵
        </button>
      </div>
    `;
    container.style.display = 'block';
    container.classList.remove('hidden');
    return;
  }

  let html = '';

  // 1. Phân hệ điều hướng (Navigation Matches - TOP PRIORITY!)
  if (data.nav && data.nav.length > 0) {
    html += `<div class="px-2 py-1 text-[10px] font-bold uppercase text-teal-400 tracking-wider flex items-center gap-1.5">
      <i data-lucide="compass" class="w-3 h-3"></i>
      <span>Chức Năng & Phân Hệ</span>
    </div>`;
    data.nav.forEach(item => {
      html += `
        <div onclick="selectSearchResult('nav', '${item.target}')" data-search-target="${item.target}"
             class="p-2.5 rounded-lg bg-teal-500/15 hover:bg-teal-500/25 border border-teal-500/30 cursor-pointer flex items-center justify-between transition-colors">
          <div class="flex items-center gap-2.5">
            <div class="w-7 h-7 rounded-lg bg-teal-500/30 flex items-center justify-center text-teal-300 shrink-0">
              <i data-lucide="${item.icon || 'arrow-right'}" class="w-4 h-4"></i>
            </div>
            <div>
              <div class="font-bold text-white text-xs">${item.title}</div>
              <div class="text-[10.5px] text-teal-300/80 truncate max-w-[150px]">${item.subtitle}</div>
            </div>
          </div>
          <span class="text-[9.5px] text-teal-400 font-semibold px-1.5 py-0.5 rounded bg-teal-500/20 font-mono shrink-0">↵ Enter</span>
        </div>
      `;
    });
  }

  // 2. Kho dược matches
  if (data.inventory && data.inventory.length > 0) {
    html += `<div class="px-2 py-1 mt-2 text-[10px] font-bold uppercase text-emerald-400 tracking-wider flex items-center gap-1.5">
      <i data-lucide="package" class="w-3 h-3"></i>
      <span>Kho Dược Supabase (${data.inventory.length})</span>
    </div>`;
    data.inventory.forEach(item => {
      html += `
        <div onclick="selectSearchResult('inventory', '${item.ma_sp}')" data-search-target="inventory"
             class="p-2 rounded-lg hover:bg-white/[0.06] cursor-pointer flex justify-between items-center transition-colors">
          <div>
            <div class="font-bold text-white">${item.ten_sp}</div>
            <div class="text-[10.5px] text-teal-300 font-mono">Mã: ${item.ma_sp} · Tồn: ${item.so_luong} đơn vị</div>
          </div>
          <div class="text-emerald-400 font-bold font-mono">${(item.gia_ban || 0).toLocaleString('vi-VN')} đ</div>
        </div>
      `;
    });
  }

  // 3. Bệnh án matches
  if (data.patients && data.patients.length > 0) {
    html += `<div class="px-2 py-1 mt-2 text-[10px] font-bold uppercase text-cyan-400 tracking-wider flex items-center gap-1.5">
      <i data-lucide="paw-print" class="w-3 h-3"></i>
      <span>Hồ Sơ Bệnh Án (${data.patients.length})</span>
    </div>`;
    data.patients.forEach(p => {
      html += `
        <div onclick="selectSearchResult('patients', '${p.id}')" data-search-target="patients"
             class="p-2 rounded-lg hover:bg-white/[0.06] cursor-pointer transition-colors">
          <div class="font-bold text-white">${p.owner_name} <span class="text-slate-400 font-normal">(${p.animal_info})</span></div>
          <div class="text-[10.5px] text-amber-300 truncate">Chẩn đoán: ${p.diagnosis}</div>
        </div>
      `;
    });
  }

  // 4. Kho tri thức matches
  if (data.knowledge && data.knowledge.length > 0) {
    html += `<div class="px-2 py-1 mt-2 text-[10px] font-bold uppercase text-purple-400 tracking-wider flex items-center gap-1.5">
      <i data-lucide="bot" class="w-3 h-3"></i>
      <span>Tư Vấn Phác Đồ RAG (${data.knowledge.length})</span>
    </div>`;
    data.knowledge.forEach(k => {
      html += `
        <div onclick="selectSearchResult('rag', '${k.title.replace(/'/g, "\\'")}')" data-search-target="rag"
             class="p-2 rounded-lg hover:bg-white/[0.06] cursor-pointer transition-colors">
          <div class="font-bold text-white text-[11px]">${k.title}</div>
          <div class="text-[10.5px] text-slate-400 truncate">${k.snippet}</div>
        </div>
      `;
    });
  }

  container.innerHTML = html;
  container.style.display = 'block';
  container.classList.remove('hidden');
  if (window.lucide) lucide.createIcons();
}

function selectSearchResult(type, param) {
  closeSearchResults();
  const searchInput = document.getElementById('globalSearchInput');
  if (searchInput) searchInput.value = '';

  if (type === 'nav') {
    switchView(param);
  } else if (type === 'inventory') {
    switchView('inventory');
    const input = document.getElementById('inventorySearchInput');
    if (input) {
      input.value = param;
      filterInventoryTable();
    }
  } else if (type === 'patients') {
    switchView('patients');
  } else if (type === 'rag') {
    switchView('rag');
    fillRagPrompt(param.startsWith('Xem phác đồ') ? param : `Tư vấn phác đồ điều trị cho ca bệnh: ${param}`);
  }
}

// ── Inventory Table Render & CRUD ──
function renderInventoryTable(items = null) {
  const data = items || state.inventory;
  const tbody = document.getElementById('inventoryTableBody');
  if (!tbody) return;

  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-slate-400">Không tìm thấy sản phẩm nào trong kho.</td></tr>`;
    return;
  }

  tbody.innerHTML = data.map(item => {
    const qty = parseInt(item.so_luong) || 0;
    const isLow = qty <= 5;
    const statusBadge = isLow
      ? `<span class="px-2 py-0.5 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-300 font-semibold text-[10px]">Sắp hết (≤5)</span>`
      : `<span class="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 font-semibold text-[10px]">Đủ hàng</span>`;

    return `
      <tr class="hover:bg-white/[0.02] transition-colors">
        <td class="py-3 px-4 font-mono text-teal-300 font-medium">${item.ma_sp}</td>
        <td class="py-3 px-4 font-semibold text-white">${item.ten_sp}</td>
        <td class="py-3 px-4 text-center">
          <div class="inline-flex items-center gap-1.5 bg-white/[0.04] px-2 py-1 rounded-lg border border-white/[0.08]">
            <button onclick="adjustQty(${item.id}, -1)" class="w-5 h-5 flex items-center justify-center rounded hover:bg-white/10 text-slate-300 text-xs font-bold">-</button>
            <span class="w-8 text-center font-bold text-white">${qty}</span>
            <button onclick="adjustQty(${item.id}, 1)" class="w-5 h-5 flex items-center justify-center rounded hover:bg-white/10 text-slate-300 text-xs font-bold">+</button>
          </div>
        </td>
        <td class="py-3 px-4 text-right text-slate-400 font-mono">${(item.gia_goc || 0).toLocaleString('vi-VN')} đ</td>
        <td class="py-3 px-4 text-right text-emerald-400 font-bold font-mono">${(item.gia_ban || 0).toLocaleString('vi-VN')} đ</td>
        <td class="py-3 px-4 text-center">${statusBadge}</td>
        <td class="py-3 px-4 text-center">
          <button onclick="deleteProduct(${item.id})" class="p-1.5 rounded text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors" title="Xóa">
            <i data-lucide="trash-2" class="w-4 h-4"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

function filterInventoryTable() {
  const query = (document.getElementById('inventorySearchInput')?.value || '').toLowerCase().trim();
  if (!query) {
    renderInventoryTable();
    return;
  }
  const filtered = state.inventory.filter(i => 
    (i.ten_sp || '').toLowerCase().includes(query) || 
    (i.ma_sp || '').toLowerCase().includes(query)
  );
  renderInventoryTable(filtered);
}

async function adjustQty(id, delta) {
  const item = state.inventory.find(x => x.id === id);
  if (!item) return;
  const newQty = Math.max(0, (parseInt(item.so_luong) || 0) + delta);
  item.so_luong = newQty;
  renderInventoryTable();

  try {
    await fetch(`/api/inventory/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ so_luong: newQty })
    });
    showToast(`Đã cập nhật ${item.ten_sp}: ${newQty} đơn vị`);
    await loadStats();
  } catch (err) {
    showToast('Lỗi cập nhật số lượng', true);
  }
}

async function deleteProduct(id) {
  if (!confirm('Bạn có chắc chắn muốn xóa sản phẩm này khỏi Supabase?')) return;
  try {
    const res = await fetch(`/api/inventory/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast('Đã xóa sản phẩm thành công');
      await loadInventory();
      await loadStats();
    }
  } catch (err) {
    showToast('Lỗi khi xóa sản phẩm', true);
  }
}

// ── Modal Handlers & Helpers ──
window.openModal = function(id) {
  const m = document.getElementById(id);
  if (m) {
    m.style.display = 'flex';
    m.classList.remove('hidden');
  }
};

window.closeModal = function(id) {
  const m = document.getElementById(id);
  if (m) {
    m.style.display = 'none';
    m.classList.add('hidden');
  }
};

// ── Modal Add Medicine ──
window.openAddMedicineModal = function() {
  window.openModal('addMedicineModal');
};

window.closeAddMedicineModal = function() {
  window.closeModal('addMedicineModal');
};

async function submitNewMedicine() {
  const ma_sp = document.getElementById('new_ma_sp')?.value.trim();
  const ten_sp = document.getElementById('new_ten_sp')?.value.trim();
  const so_luong = parseInt(document.getElementById('new_so_luong')?.value) || 0;
  const gia_goc = parseInt(document.getElementById('new_gia_goc')?.value) || 0;
  const gia_ban = parseInt(document.getElementById('new_gia_ban')?.value) || 0;

  if (!ma_sp || !ten_sp) {
    alert('Vui lòng nhập đầy đủ Mã sản phẩm và Tên sản phẩm');
    return;
  }

  try {
    const res = await fetch('/api/inventory', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ma_sp, ten_sp, so_luong, gia_goc, gia_ban })
    });
    const result = await res.json();
    if (result.success) {
      showToast(`Đã thêm mới vào Supabase: ${ten_sp}`);
      closeAddMedicineModal();
      document.getElementById('new_ma_sp').value = '';
      document.getElementById('new_ten_sp').value = '';
      await loadInventory();
      await loadStats();
    }
  } catch (err) {
    showToast('Lỗi khi thêm sản phẩm vào Supabase', true);
  }
}

function exportInventoryCSV() {
  if (!state.inventory || state.inventory.length === 0) {
    alert('Kho hàng chưa có dữ liệu để xuất');
    return;
  }
  let csv = 'Mã SP,Tên Sản Phẩm,Số Lượng,Giá Gốc (đ),Giá Bán (đ)\n';
  state.inventory.forEach(i => {
    csv += `"${i.ma_sp}","${i.ten_sp}",${i.so_luong},${i.gia_goc},${i.gia_ban}\n`;
  });
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Kho_Duoc_Tung_Thao_${new Date().toISOString().slice(0,10)}.csv`;
  a.click();
  showToast('Đã xuất file CSV thành công');
}

// ── Real Patient Records (Zero Mock Data!) ──
function renderPatientsGrid() {
  const container = document.getElementById('patientCardsContainer');
  if (!container) return;

  if (!state.patients || state.patients.length === 0) {
    container.innerHTML = `
      <div class="col-span-full p-8 text-center glass-card border-dashed border-white/[0.1] rounded-2xl space-y-3">
        <div class="w-12 h-12 mx-auto rounded-2xl bg-white/[0.03] border border-white/[0.08] flex items-center justify-center text-slate-400">
          <i data-lucide="clipboard-list" class="w-6 h-6 text-teal-400"></i>
        </div>
        <h4 class="text-sm font-bold text-white">Chưa Có Hồ Sơ Bệnh Án Nào Được Tạo</h4>
        <p class="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
          Lập hồ sơ bệnh án để theo dõi chi tiết lịch sử khám bệnh, đàn gia súc/gia cầm, đơn thuốc đã kê và lịch hẹn tái khám của khách hàng thực tế.
        </p>
        <button onclick="openAddPatientModal()" class="px-4 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-white text-xs font-bold inline-flex items-center gap-2 shadow-lg shadow-teal-500/20">
          <i data-lucide="plus" class="w-3.5 h-3.5"></i>
          <span>+ Lập Bệnh Án Đầu Tiên</span>
        </button>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  container.innerHTML = state.patients.map(p => `
    <div class="glass-card p-4 space-y-2 text-xs relative group">
      <div class="flex items-center justify-between">
        <span class="font-bold text-white text-sm">${p.owner_name}</span>
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-300 text-[10px] font-semibold">${p.status}</span>
          <button onclick="deletePatientRecord(${p.id})" class="text-slate-400 hover:text-rose-400 p-1" title="Xóa hồ sơ">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>
      ${p.phone ? `<div class="text-[11px] text-slate-400">📞 SĐT: <span class="text-slate-300 font-mono">${p.phone}</span></div>` : ''}
      <div class="text-slate-300">🐾 <span class="font-medium">${p.animal_info}</span></div>
      <div class="text-slate-400">🩺 Chẩn đoán: <span class="text-amber-300 font-medium">${p.diagnosis}</span></div>
      <div class="text-slate-400">💊 Thuốc kê: <span class="text-emerald-300 font-medium">${p.prescription}</span></div>
      <div class="text-[10px] text-slate-400 pt-2 border-t border-white/[0.05] flex justify-between">
        <span>Tạo ngày: ${p.created_at || 'Mới'}</span>
        ${p.followup_date ? `<span class="text-cyan-300 font-medium">Tái khám: ${p.followup_date}</span>` : ''}
      </div>
    </div>
  `).join('');

  if (window.lucide) lucide.createIcons();
}

window.openAddPatientModal = function() {
  window.openModal('addPatientModal');
};

window.closeAddPatientModal = function() {
  window.closeModal('addPatientModal');
};

async function submitNewPatient() {
  const owner_name = document.getElementById('patient_owner')?.value.trim();
  const phone = document.getElementById('patient_phone')?.value.trim();
  const animal_info = document.getElementById('patient_animal')?.value.trim();
  const diagnosis = document.getElementById('patient_diagnosis')?.value.trim();
  const prescription = document.getElementById('patient_prescription')?.value.trim();
  const status = document.getElementById('patient_status')?.value;
  const followup_date = document.getElementById('patient_followup')?.value;
  const notes = document.getElementById('patient_notes')?.value.trim();

  if (!owner_name || !animal_info || !diagnosis || !prescription) {
    alert('Vui lòng điền đầy đủ Tên chủ nuôi, Vật nuôi, Chẩn đoán và Thuốc kê');
    return;
  }

  try {
    const res = await fetch('/api/patients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        owner_name, phone, animal_info, diagnosis, prescription, status, followup_date, notes
      })
    });
    const result = await res.json();
    if (result.success) {
      showToast(`Đã lưu bệnh án: ${owner_name}`);
      closeAddPatientModal();
      // Clear inputs
      document.getElementById('patient_owner').value = '';
      document.getElementById('patient_phone').value = '';
      document.getElementById('patient_animal').value = '';
      document.getElementById('patient_diagnosis').value = '';
      document.getElementById('patient_prescription').value = '';
      document.getElementById('patient_notes').value = '';

      await loadPatients();
      await loadStats();
    }
  } catch (err) {
    showToast('Lỗi khi lưu bệnh án', true);
  }
}

async function deletePatientRecord(id) {
  if (!confirm('Bạn có chắc chắn muốn xóa hồ sơ bệnh án này?')) return;
  try {
    const res = await fetch(`/api/patients/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast('Đã xóa hồ sơ bệnh án');
      await loadPatients();
      await loadStats();
    }
  } catch (err) {
    showToast('Lỗi khi xóa bệnh án', true);
  }
}

// ── Real Sales & Revenue Management ──
function renderSalesTable() {
  const tbody = document.getElementById('salesTableBody');
  if (!tbody) return;

  if (!state.sales || state.sales.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-slate-400">Chưa có giao dịch bán hàng nào được ghi nhận. Bấm "+ Ghi Nhận Doanh Thu Mới" để bắt đầu.</td></tr>`;
    return;
  }

  tbody.innerHTML = state.sales.map(s => `
    <tr class="hover:bg-white/[0.02] transition-colors">
      <td class="py-3 px-4 font-mono text-slate-300">${s.date}</td>
      <td class="py-3 px-4 font-semibold text-white">${s.description}</td>
      <td class="py-3 px-4 text-slate-300">${s.customer || 'Khách lẻ'}</td>
      <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-white/[0.05] text-[10.5px] text-teal-300">${s.category}</span></td>
      <td class="py-3 px-4 text-right font-mono font-bold text-emerald-400">+${(s.amount || 0).toLocaleString('vi-VN')} đ</td>
      <td class="py-3 px-4 text-center">
        <button onclick="deleteSaleRecord(${s.id})" class="p-1 rounded text-slate-400 hover:text-rose-400" title="Xóa giao dịch">
          <i data-lucide="trash-2" class="w-4 h-4"></i>
        </button>
      </td>
    </tr>
  `).join('');

  if (window.lucide) lucide.createIcons();
}

window.openAddSaleModal = function() {
  const d = document.getElementById('sale_date');
  if (d && !d.value) d.value = new Date().toISOString().slice(0, 10);
  window.openModal('addSaleModal');
};

window.closeAddSaleModal = function() {
  window.closeModal('addSaleModal');
};

async function submitNewSale() {
  const amount = parseInt(document.getElementById('sale_amount')?.value) || 0;
  const description = document.getElementById('sale_desc')?.value.trim();
  const customer = document.getElementById('sale_customer')?.value.trim();
  const category = document.getElementById('sale_category')?.value;
  const date = document.getElementById('sale_date')?.value;

  if (amount <= 0 || !description) {
    alert('Vui lòng nhập số tiền hợp lệ và nội dung giao dịch');
    return;
  }

  try {
    const res = await fetch('/api/sales', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, description, customer, category, date })
    });
    const result = await res.json();
    if (result.success) {
      showToast(`Đã ghi nhận doanh thu: +${amount.toLocaleString('vi-VN')} đ`);
      closeAddSaleModal();
      document.getElementById('sale_amount').value = '';
      document.getElementById('sale_desc').value = '';
      document.getElementById('sale_customer').value = '';
      await loadSales();
      await loadStats();
    }
  } catch (err) {
    showToast('Lỗi khi ghi nhận doanh thu', true);
  }
}

async function deleteSaleRecord(id) {
  if (!confirm('Bạn có chắc chắn muốn xóa giao dịch này khỏi sổ quỹ?')) return;
  try {
    const res = await fetch(`/api/sales/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast('Đã xóa giao dịch doanh thu');
      await loadSales();
      await loadStats();
    }
  } catch (err) {
    showToast('Lỗi xóa giao dịch', true);
  }
}

// ── Monthly Goal Target Modal ──
window.openEditGoalModal = function() {
  const currentTarget = state.stats?.monthly_goal_target || 50000000;
  const input = document.getElementById('input_monthly_goal_target');
  if (input) input.value = currentTarget;
  window.openModal('editGoalModal');
};

window.closeEditGoalModal = function() {
  window.closeModal('editGoalModal');
};

async function submitEditGoal() {
  const target = parseInt(document.getElementById('input_monthly_goal_target')?.value) || 0;
  if (target <= 0) {
    alert('Vui lòng nhập chỉ tiêu lớn hơn 0');
    return;
  }
  try {
    const res = await fetch('/api/goal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target })
    });
    const d = await res.json();
    if (d.success) {
      showToast('Đã cập nhật chỉ tiêu doanh thu tháng!');
      closeEditGoalModal();
      await loadStats();
    }
  } catch (err) {
    showToast('Lỗi cập nhật chỉ tiêu', true);
  }
}

// ── Chart.js Sales Studio with Real Data & Empty State ──
function renderSalesChart(points) {
  const emptyPlaceholder = document.getElementById('chartEmptyState');
  const canvas = document.getElementById('salesChart');

  if (!points || points.length === 0) {
    if (emptyPlaceholder) {
      emptyPlaceholder.style.display = 'flex';
      emptyPlaceholder.classList.remove('hidden');
    }
    if (canvas) {
      canvas.style.display = 'none';
      canvas.classList.add('hidden');
    }
    if (state.chartInstance) {
      state.chartInstance.destroy();
      state.chartInstance = null;
    }
    return;
  }

  // Real data points exist
  if (emptyPlaceholder) {
    emptyPlaceholder.style.display = 'none';
    emptyPlaceholder.classList.add('hidden');
  }
  if (canvas) {
    canvas.style.display = 'block';
    canvas.classList.remove('hidden');
  }

  const ctx = canvas?.getContext('2d');
  if (!ctx) return;

  const gradient = ctx.createLinearGradient(0, 0, 0, 240);
  gradient.addColorStop(0, 'rgba(15, 118, 110, 0.5)');
  gradient.addColorStop(0.5, 'rgba(16, 185, 129, 0.15)');
  gradient.addColorStop(1, 'rgba(6, 182, 212, 0.0)');

  const labels = points.map(p => p.label);
  const data = points.map(p => p.amount);

  if (state.chartInstance) {
    state.chartInstance.destroy();
  }

  state.chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Doanh thu (VNĐ)',
        data: data,
        borderColor: '#2dd4bf',
        borderWidth: 2.5,
        backgroundColor: gradient,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#0f766e',
        pointBorderColor: '#2dd4bf',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(13, 19, 33, 0.95)',
          borderColor: 'rgba(255, 255, 255, 0.12)',
          borderWidth: 1,
          titleFont: { family: 'Plus Jakarta Sans', size: 11 },
          bodyFont: { family: 'Plus Jakarta Sans', size: 12, weight: 'bold' },
          callbacks: {
            label: (ctx) => `${ctx.parsed.y.toLocaleString('vi-VN')} đ`
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.03)' },
          ticks: { color: '#64748b', font: { size: 10 } }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.03)' },
          ticks: {
            color: '#64748b',
            font: { size: 10 },
            callback: (v) => `${(v / 1000).toLocaleString('vi-VN')}k`
          }
        }
      }
    }
  });
}

function setChartPeriod(period) {
  state.chartPeriod = period;
  const btnMonth = document.getElementById('btn-chart-month');
  const btnWeek = document.getElementById('btn-chart-week');
  if (period === 'month') {
    btnMonth?.classList.add('active');
    btnWeek?.classList.remove('active');
  } else {
    btnWeek?.classList.add('active');
    btnMonth?.classList.remove('active');
  }
}

// ── RAG AI Consultation ──
function fillRagPrompt(text) {
  const input = document.getElementById('ragQueryInput');
  if (input) input.value = text;
}

async function submitRagConsult() {
  const query = document.getElementById('ragQueryInput')?.value.trim();
  if (!query) {
    alert('Vui lòng nhập triệu chứng vật nuôi trước khi gửi.');
    return;
  }

  const btn = document.getElementById('btnSubmitRag');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin mr-1">⏳</span> Đang chẩn đoán...`;
  }

  try {
    const res = await fetch('/api/ai/consult', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const data = await res.json();

    const container = document.getElementById('ragResponseContainer');
    const content = document.getElementById('ragResponseContent');
    if (container && content) {
      container.classList.remove('hidden');
      content.textContent = data.answer;
      showToast('Đã hoàn thành lập phác đồ điều trị');
      await loadStats(); // Update consultation counter
    }
  } catch (err) {
    showToast('Lỗi kết nối bác sĩ AI', true);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="send" class="w-3.5 h-3.5"></i><span>Lập Phác Đồ Điều Trị</span>`;
      if (window.lucide) lucide.createIcons();
    }
  }
}

function copyRagResponse() {
  const text = document.getElementById('ragResponseContent')?.textContent;
  if (text) {
    navigator.clipboard.writeText(text);
    showToast('Đã sao chép phác đồ vào clipboard');
  }
}

// ── Shopee SEO Generator ──
function cleanShopeePlainText(raw) {
  if (!raw) return '';
  return raw
    .replace(/\*{1,3}(.*?)\*{1,3}/g, '$1')
    .replace(/^[ \t]*\*[ \t]+/gm, '- ')
    .replace(/\*/g, '')
    .replace(/^[ \t]*#{1,6}[ \t]*/gm, '')
    .replace(/^[ \t]*[-=_]{3,}[ \t]*$/gm, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

async function generateShopeePost() {
  const name = document.getElementById('shopeeProductNameInput')?.value.trim();
  if (!name) {
    alert('Vui lòng nhập tên sản phẩm cần tạo bài đăng Shopee.');
    return;
  }

  const btn = document.getElementById('btnGenerateShopee');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin mr-1">⏳</span> Đang tạo bài...`;
  }

  try {
    const res = await fetch('/api/ai/shopee', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_name: name })
    });
    const data = await res.json();

    const container = document.getElementById('shopeeResultContainer');
    const resultText = document.getElementById('shopeeResultText');
    const techText = document.getElementById('shopeeTechInfoText');

    if (container && resultText && techText) {
      container.classList.remove('hidden');
      resultText.value = cleanShopeePlainText(data.shopee_content);
      techText.textContent = data.technical_info;
      showToast('Đã tạo bài đăng Shopee chuẩn SEO (Plain Text sạch)');
    }
  } catch (err) {
    showToast('Lỗi khi tạo bài Shopee', true);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5"></i><span>Tạo Bài Chuẩn SEO</span>`;
      if (window.lucide) lucide.createIcons();
    }
  }
}

window.copyShopeePost = function() {
  const text = document.getElementById('shopeeResultText')?.value;
  if (!text || !text.trim()) {
    showToast('Chưa có nội dung bài đăng để sao chép', true);
    return;
  }
  const clean = cleanShopeePlainText(text);
  navigator.clipboard.writeText(clean);
  showToast('✓ Đã sao chép bài đăng Shopee (Plain Text sạch, 0 dấu *)!');
};

// ── AI Model Configuration & Switching ──
function formatModelDisplayName(model, effort) {
  let name = model || 'Gemini 3.8 Flash';
  if (name.includes('gemini-3.8-flash') || name.includes('gemini-3.8')) name = 'Gemini 3.8 Flash';
  else if (name.includes('gemini-2.5-flash')) name = 'Gemini 2.5 Flash';
  else if (name.includes('gemini-2.5-pro')) name = 'Gemini 2.5 Pro';
  
  if (effort && effort !== 'none') {
    name += ` (${effort.charAt(0).toUpperCase() + effort.slice(1)})`;
  }
  return name;
}

function updateModelDisplayUI(modelName, effort) {
  const displayTitle = formatModelDisplayName(modelName, effort);
  
  const headerText = document.getElementById('headerModelText');
  if (headerText) headerText.textContent = displayTitle;

  const currentBadge = document.getElementById('currentModelBadgeText');
  if (currentBadge) currentBadge.textContent = displayTitle;

  const settingActive = document.getElementById('settingActiveModelName');
  if (settingActive) settingActive.textContent = `${modelName} (${effort || 'high'})`;

  const selectModel = document.getElementById('selectAiModel');
  const customContainer = document.getElementById('customModelContainer');
  const customInput = document.getElementById('inputCustomModel');

  if (selectModel) {
    if (['google/gemini-3.8-flash', 'google/gemini-2.5-flash', 'google/gemini-2.5-pro'].includes(modelName)) {
      selectModel.value = modelName;
      if (customContainer) customContainer.classList.add('hidden');
    } else {
      selectModel.value = 'custom';
      if (customContainer) customContainer.classList.remove('hidden');
      if (customInput) customInput.value = modelName;
    }
  }

  const selectEffort = document.getElementById('selectReasoningEffort');
  if (selectEffort && effort) {
    selectEffort.value = effort;
  }
}

window.handleModelPresetChange = function() {
  const select = document.getElementById('selectAiModel');
  const customContainer = document.getElementById('customModelContainer');
  if (select && customContainer) {
    if (select.value === 'custom') {
      customContainer.classList.remove('hidden');
      document.getElementById('inputCustomModel')?.focus();
    } else {
      customContainer.classList.add('hidden');
    }
  }
};

window.applyModelChange = async function() {
  const select = document.getElementById('selectAiModel');
  const customInput = document.getElementById('inputCustomModel');
  const selectEffort = document.getElementById('selectReasoningEffort');

  let chosenModel = select?.value;
  if (chosenModel === 'custom') {
    chosenModel = customInput?.value.trim();
  }
  const chosenEffort = selectEffort?.value || 'high';

  if (!chosenModel) {
    alert('Vui lòng chọn hoặc nhập tên mô hình AI hợp lệ');
    return;
  }

  try {
    const res = await fetch('/api/settings/model', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: chosenModel, reasoning_effort: chosenEffort })
    });
    const d = await res.json();
    if (d.success) {
      updateModelDisplayUI(d.model, d.reasoning_effort);
      showToast(`Đã chuyển sang mô hình: ${formatModelDisplayName(d.model, d.reasoning_effort)}`);
    } else {
      showToast(d.detail || 'Lỗi chuyển đổi model', true);
    }
  } catch (err) {
    showToast('Lỗi kết nối khi đổi model', true);
  }
};

// ── Save API Key ──
async function saveApiKey() {
  const key = document.getElementById('inputApiKeySetting')?.value.trim();
  if (!key) return;
  try {
    const res = await fetch('/api/settings/key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: key })
    });
    const d = await res.json();
    if (d.success) {
      showToast('Đã cập nhật API Key thành công!');
    }
  } catch (err) {
    showToast('Lỗi lưu Key', true);
  }
}

// ── Toast Notifications ──
function showToast(message, isError = false) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `p-3.5 rounded-xl border text-xs font-semibold shadow-2xl backdrop-blur-xl transition-all duration-300 pointer-events-auto flex items-center gap-2 ${
    isError 
      ? 'bg-rose-950/80 border-rose-500/40 text-rose-200' 
      : 'bg-emerald-950/80 border-emerald-500/40 text-emerald-200'
  }`;
  toast.innerHTML = `<span>${isError ? '⚠️' : '✓'}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}
