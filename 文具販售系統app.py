from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# 建立模擬資料庫
products = [
    {"id": 1, "name": "鉛筆",   "price": 30, "stock": 100, "category": "書寫工具", "description": "HB 標準鉛筆，適合日常書寫與素描"},
    {"id": 2, "name": "紅筆",   "price": 35, "stock": 80,  "category": "書寫工具", "description": "油性紅色原子筆，書寫流暢不暈染"},
    {"id": 3, "name": "藍筆",   "price": 35, "stock": 90,  "category": "書寫工具", "description": "油性藍色原子筆，適合正式文件簽署"},
    {"id": 4, "name": "自動鉛筆","price": 35, "stock": 60,  "category": "書寫工具", "description": "0.5mm 自動鉛筆，附橡皮擦蓋"},
    {"id": 5, "name": "橡皮擦", "price": 15, "stock": 150, "category": "文具配件", "description": "無毒橡皮擦，擦拭乾淨不留痕"},
    {"id": 6, "name": "直尺",   "price": 20, "stock": 70,  "category": "文具配件", "description": "30cm 透明塑膠直尺，刻度清晰"},
    {"id": 7, "name": "剪刀",   "price": 50, "stock": 40,  "category": "辦公用品", "description": "不鏽鋼刀刃剪刀，安全圓頭設計"},
    {"id": 8, "name": "膠水",   "price": 25, "stock": 55,  "category": "辦公用品", "description": "固體口紅膠，不沾手使用方便"},
]

# ─────────────────────────────
# 輔助函式
# ─────────────────────────────
def find_product(pid: int):
    for p in products:
        if p["id"] == pid:
            return p
    return None

def name_exists(name: str, exclude_id: int = None):
    for p in products:
        if p["name"] == name and p["id"] != exclude_id:
            return True
    return False


# ─────────────────────────────
# HTML 前端（單頁應用）
# ─────────────────────────────
HTML = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>🖊️ 文具販賣系統</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #f0f4f8; color: #333; }

    /* ── 導覽列 ── */
    header {
      background: linear-gradient(135deg, #2563eb, #1e40af);
      color: #fff; padding: 16px 32px;
      display: flex; align-items: center; gap: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,.25);
    }
    header h1 { font-size: 1.5rem; }
    nav { margin-left: auto; display: flex; gap: 10px; }
    nav button {
      background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.4);
      color: #fff; padding: 6px 16px; border-radius: 20px; cursor: pointer;
      font-size: .9rem; transition: background .2s;
    }
    nav button:hover { background: rgba(255,255,255,.3); }

    /* ── 主容器 ── */
    main { max-width: 1100px; margin: 30px auto; padding: 0 20px; }

    /* ── 卡片面板 ── */
    .panel {
      background: #fff; border-radius: 12px;
      box-shadow: 0 2px 10px rgba(0,0,0,.08);
      padding: 24px; margin-bottom: 24px;
    }
    .panel h2 { font-size: 1.15rem; margin-bottom: 16px; color: #1e40af; }

    /* ── 搜尋列 ── */
    .search-bar { display: flex; gap: 10px; margin-bottom: 20px; }
    .search-bar input {
      flex: 1; padding: 10px 14px; border: 1px solid #d1d5db;
      border-radius: 8px; font-size: 1rem;
    }
    .search-bar input:focus { outline: none; border-color: #2563eb; }

    /* ── 按鈕 ── */
    .btn {
      padding: 9px 20px; border: none; border-radius: 8px;
      cursor: pointer; font-size: .95rem; font-weight: 600;
      transition: opacity .2s, transform .1s;
    }
    .btn:hover { opacity: .88; transform: translateY(-1px); }
    .btn-primary   { background: #2563eb; color: #fff; }
    .btn-success   { background: #16a34a; color: #fff; }
    .btn-danger    { background: #dc2626; color: #fff; }
    .btn-warning   { background: #d97706; color: #fff; }
    .btn-secondary { background: #6b7280; color: #fff; }

    /* ── 表格 ── */
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 12px 14px; text-align: left; border-bottom: 1px solid #e5e7eb; }
    th { background: #eff6ff; color: #1e40af; font-weight: 700; }
    tr:hover td { background: #f8fafc; }
    .badge {
      display: inline-block; padding: 2px 10px; border-radius: 12px;
      font-size: .78rem; font-weight: 600;
    }
    .badge-blue   { background: #dbeafe; color: #1e40af; }
    .badge-green  { background: #dcfce7; color: #16a34a; }
    .badge-orange { background: #fff7ed; color: #c2410c; }

    /* ── 表單 ── */
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .form-group { display: flex; flex-direction: column; gap: 5px; }
    .form-group label { font-size: .88rem; font-weight: 600; color: #374151; }
    .form-group input, .form-group select {
      padding: 9px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: .95rem;
    }
    .form-group input:focus, .form-group select:focus { outline: none; border-color: #2563eb; }
    .form-actions { display: flex; gap: 10px; margin-top: 16px; }

    /* ── 訊息提示 ── */
    #toast {
      position: fixed; bottom: 30px; right: 30px;
      background: #1e293b; color: #fff; padding: 12px 22px;
      border-radius: 10px; font-size: .95rem;
      opacity: 0; pointer-events: none; transition: opacity .3s;
      box-shadow: 0 4px 14px rgba(0,0,0,.3); z-index: 999;
    }
    #toast.show { opacity: 1; }

    /* ── 統計卡 ── */
    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .stat-card {
      background: #fff; border-radius: 12px; padding: 20px 24px;
      box-shadow: 0 2px 8px rgba(0,0,0,.07); border-left: 4px solid #2563eb;
    }
    .stat-card .label { font-size: .82rem; color: #6b7280; margin-bottom: 4px; }
    .stat-card .value { font-size: 1.7rem; font-weight: 700; color: #1e40af; }

    /* ── 分頁 ── */
    .section { display: none; }
    .section.active { display: block; }
  </style>
</head>
<body>

<header>
  <span style="font-size:1.8rem">🖊️</span>
  <h1>文具販賣系統</h1>
  <nav>
    <button onclick="showSection('list')">📋 商品列表</button>
    <button onclick="showSection('add')">➕ 新增商品</button>
    <button onclick="showSection('search')">🔍 查詢商品</button>
  </nav>
</header>

<main>

  <!-- 統計卡 -->
  <div class="stats" id="statsArea"></div>

  <!-- ① 商品列表 -->
  <div class="section active" id="sec-list">
    <div class="panel">
      <h2>📋 所有商品</h2>
      <table id="productTable">
        <thead>
          <tr>
            <th>ID</th><th>商品名稱</th><th>分類</th>
            <th>價格 (NT$)</th><th>庫存</th><th>描述</th><th>操作</th>
          </tr>
        </thead>
        <tbody id="productBody"></tbody>
      </table>
    </div>
  </div>

  <!-- ② 新增商品 -->
  <div class="section" id="sec-add">
    <div class="panel">
      <h2>➕ 新增商品</h2>
      <div class="form-grid">
        <div class="form-group">
          <label>商品名稱</label>
          <input id="addName" placeholder="例：藍色原子筆" />
        </div>
        <div class="form-group">
          <label>分類</label>
          <select id="addCategory">
            <option>書寫工具</option>
            <option>文具配件</option>
            <option>辦公用品</option>
          </select>
        </div>
        <div class="form-group">
          <label>價格 (NT$)</label>
          <input id="addPrice" type="number" min="1" placeholder="30" />
        </div>
        <div class="form-group">
          <label>庫存數量</label>
          <input id="addStock" type="number" min="0" placeholder="100" />
        </div>
        <div class="form-group" style="grid-column: 1 / -1;">
          <label>描述</label>
          <input id="addDesc" placeholder="例：0.5mm 自動鉛筆，附橡皮擦蓋" />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn btn-success" onclick="addProduct()">✅ 新增</button>
        <button class="btn btn-secondary" onclick="clearAddForm()">🔄 清除</button>
      </div>
    </div>
  </div>

  <!-- ③ 查詢商品 -->
  <div class="section" id="sec-search">
    <div class="panel">
      <h2>🔍 以 ID 查詢商品</h2>
      <div class="search-bar">
        <input id="searchId" type="number" min="1" placeholder="輸入商品 ID" />
        <button class="btn btn-primary" onclick="searchById()">查詢</button>
      </div>
      <div id="searchResult"></div>
    </div>
  </div>

  <!-- 編輯 Modal（行內展開） -->
  <div class="panel" id="editPanel" style="display:none; border:2px solid #2563eb;">
    <h2>✏️ 編輯商品</h2>
    <input type="hidden" id="editId" />
    <div class="form-grid">
      <div class="form-group">
        <label>商品名稱</label>
        <input id="editName" />
      </div>
      <div class="form-group">
        <label>分類</label>
        <select id="editCategory">
          <option>書寫工具</option>
          <option>文具配件</option>
          <option>辦公用品</option>
        </select>
      </div>
      <div class="form-group">
        <label>價格 (NT$)</label>
        <input id="editPrice" type="number" />
      </div>
      <div class="form-group">
        <label>庫存</label>
        <input id="editStock" type="number" />
      </div>
      <div class="form-group" style="grid-column: 1 / -1;">
        <label>描述</label>
        <input id="editDesc" placeholder="商品描述" />
      </div>
    </div>
    <div class="form-actions">
      <button class="btn btn-warning" onclick="saveEdit()">💾 儲存</button>
      <button class="btn btn-secondary" onclick="cancelEdit()">❌ 取消</button>
    </div>
  </div>

</main>

<div id="toast"></div>

<script>
// ── 工具 ──────────────────────────────────────
function toast(msg, ok = true) {
  const el = document.getElementById('toast');
  el.textContent = (ok ? '✅ ' : '❌ ') + msg;
  el.className = 'show';
  setTimeout(() => el.className = '', 2800);
}

function showSection(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.getElementById('sec-' + name).classList.add('active');
  document.getElementById('editPanel').style.display = 'none';
}

// ── API 呼叫 ──────────────────────────────────
async function api(path, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  return res.json();
}

// ── 載入商品列表 ─────────────────────────────
async function loadProducts() {
  const data = await api('/products');
  renderTable(data);
  renderStats(data);
}

function renderStats(products) {
  const total = products.length;
  const totalStock = products.reduce((s, p) => s + p.stock, 0);
  const avgPrice = total ? Math.round(products.reduce((s, p) => s + p.price, 0) / total) : 0;
  const lowStock = products.filter(p => p.stock < 50).length;

  document.getElementById('statsArea').innerHTML = `
    <div class="stat-card"><div class="label">商品種類</div><div class="value">${total}</div></div>
    <div class="stat-card"><div class="label">總庫存</div><div class="value">${totalStock}</div></div>
    <div class="stat-card" style="border-color:#16a34a"><div class="label">平均售價</div><div class="value">$${avgPrice}</div></div>
    <div class="stat-card" style="border-color:#dc2626"><div class="label">低庫存商品</div><div class="value">${lowStock}</div></div>
  `;
}

function categoryBadge(cat) {
  const map = { '書寫工具': 'badge-blue', '文具配件': 'badge-green', '辦公用品': 'badge-orange' };
  return `<span class="badge ${map[cat] || 'badge-blue'}">${cat}</span>`;
}

function stockColor(s) {
  if (s >= 80) return '#16a34a';
  if (s >= 40) return '#d97706';
  return '#dc2626';
}

function renderTable(products) {
  const tbody = document.getElementById('productBody');
  if (!products.length) { tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#9ca3af;">尚無商品</td></tr>'; return; }
  tbody.innerHTML = products.map(p => `
    <tr>
      <td><b>${p.id}</b></td>
      <td>${p.name}</td>
      <td>${categoryBadge(p.category)}</td>
      <td>$${p.price}</td>
      <td style="color:${stockColor(p.stock)};font-weight:700">${p.stock}</td>
      <td style="color:#6b7280;font-size:.88rem;max-width:200px">${p.description || '—'}</td>
      <td style="display:flex;gap:6px">
        <button class="btn btn-warning" style="padding:5px 12px;font-size:.82rem" onclick="openEdit(${p.id})">✏️ 編輯</button>
        <button class="btn btn-danger"  style="padding:5px 12px;font-size:.82rem" onclick="deleteProduct(${p.id})">🗑️ 刪除</button>
      </td>
    </tr>
  `).join('');
}

// ── 新增商品 ──────────────────────────────────
async function addProduct() {
  const name     = document.getElementById('addName').value.trim();
  const category = document.getElementById('addCategory').value;
  const price    = parseInt(document.getElementById('addPrice').value);
  const stock    = parseInt(document.getElementById('addStock').value);
  const description = document.getElementById('addDesc').value.trim();

  if (!name || isNaN(price) || isNaN(stock)) { toast('請填寫完整資訊', false); return; }

  const res = await api('/products', 'POST', { name, category, price, stock, description });
  if (res.error) { toast(res.error, false); return; }
  toast(res.message || '新增成功');
  clearAddForm();
  loadProducts();
}

function clearAddForm() {
  ['addName','addPrice','addStock','addDesc'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('addCategory').selectedIndex = 0;
}

// ── 刪除商品 ──────────────────────────────────
async function deleteProduct(id) {
  if (!confirm(`確定刪除 ID=${id} 的商品？`)) return;
  const res = await api(`/products/${id}`, 'DELETE');
  toast(res.message || '刪除成功');
  loadProducts();
}

// ── 編輯商品 ──────────────────────────────────
async function openEdit(id) {
  const p = await api(`/products/${id}`);
  if (!p.id) { toast('找不到商品', false); return; }
  document.getElementById('editId').value       = p.id;
  document.getElementById('editName').value     = p.name;
  document.getElementById('editPrice').value    = p.price;
  document.getElementById('editStock').value    = p.stock;
  document.getElementById('editDesc').value     = p.description || '';
  const sel = document.getElementById('editCategory');
  [...sel.options].forEach((o,i) => { if(o.value === p.category) sel.selectedIndex = i; });
  document.getElementById('editPanel').style.display = 'block';
  document.getElementById('editPanel').scrollIntoView({ behavior: 'smooth' });
}

async function saveEdit() {
  const id          = parseInt(document.getElementById('editId').value);
  const name        = document.getElementById('editName').value.trim();
  const category    = document.getElementById('editCategory').value;
  const price       = parseInt(document.getElementById('editPrice').value);
  const stock       = parseInt(document.getElementById('editStock').value);
  const description = document.getElementById('editDesc').value.trim();

  if (!name || isNaN(price) || isNaN(stock)) { toast('請填寫完整資訊', false); return; }
  const res = await api(`/products/${id}`, 'PUT', { name, category, price, stock, description });
  if (res.error) { toast(res.error, false); return; }
  toast(res.message || '更新成功');
  cancelEdit();
  loadProducts();
}

function cancelEdit() {
  document.getElementById('editPanel').style.display = 'none';
}

// ── 以 ID 查詢 ────────────────────────────────
async function searchById() {
  const id  = parseInt(document.getElementById('searchId').value);
  const div = document.getElementById('searchResult');
  if (isNaN(id)) { div.innerHTML = '<p style="color:#dc2626">請輸入有效的 ID</p>'; return; }

  const p = await api(`/products/${id}`);
  if (!p.id) {
    div.innerHTML = `<p style="color:#dc2626;margin-top:10px">❌ 找不到 ID=${id} 的商品</p>`;
    return;
  }
  div.innerHTML = `
    <table style="margin-top:10px">
      <thead><tr><th>ID</th><th>名稱</th><th>分類</th><th>價格</th><th>庫存</th><th>描述</th></tr></thead>
      <tbody>
        <tr>
          <td><b>${p.id}</b></td><td>${p.name}</td>
          <td>${categoryBadge(p.category)}</td>
          <td>$${p.price}</td>
          <td style="color:${stockColor(p.stock)};font-weight:700">${p.stock}</td>
          <td style="color:#6b7280;font-size:.88rem">${p.description || '—'}</td>
        </tr>
      </tbody>
    </table>`;
}

// ── Enter 鍵觸發搜尋 ─────────────────────────
document.getElementById('searchId').addEventListener('keydown', e => {
  if (e.key === 'Enter') searchById();
});

// ── 初始化 ───────────────────────────────────
loadProducts();
</script>
</body>
</html>
"""


# ─────────────────────────────
# 路由
# ─────────────────────────────

# 首頁 → 返回 SPA
@app.route('/')
def home():
    return render_template_string(HTML)


# GET  /products          取得所有商品
@app.route('/products', methods=['GET'])
def get_all_products():
    return jsonify(products)


# GET  /products/<id>     以 id 查詢單一商品
@app.route('/products/<int:pid>', methods=['GET'])
def get_product(pid):
    p = find_product(pid)
    if p:
        return jsonify(p)
    return jsonify({"error": "找不到商品"}), 404


# POST /products          新增商品
@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data or not data.get('name') or data.get('price') is None:
        return jsonify({"error": "缺少必要欄位 (name, price)"}), 400

    name = data['name'].strip()
    if name_exists(name):
        return jsonify({"error": f"商品『{name}』已存在，無法重複新增！"}), 409

    new_id = max((p['id'] for p in products), default=0) + 1
    new_product = {
        "id":          new_id,
        "name":        name,
        "price":       int(data['price']),
        "stock":       int(data.get('stock', 0)),
        "category":    data.get('category', '其他'),
        "description": data.get('description', '').strip(),
    }
    products.append(new_product)
    return jsonify({"message": f"商品『{new_product['name']}』已新增", "product": new_product}), 201


# PUT  /products/<id>     更新商品
@app.route('/products/<int:pid>', methods=['PUT'])
def update_product(pid):
    p = find_product(pid)
    if not p:
        return jsonify({"error": "找不到商品"}), 404

    data = request.get_json()
    new_name = data.get('name', p['name']).strip()

    # 名稱重複檢查（排除自己）
    if new_name != p['name'] and name_exists(new_name, exclude_id=pid):
        return jsonify({"error": f"商品『{new_name}』已存在，無法使用相同名稱！"}), 409

    p['name']        = new_name
    p['price']       = int(data.get('price',       p['price']))
    p['stock']       = int(data.get('stock',        p['stock']))
    p['category']    = data.get('category',         p['category'])
    p['description'] = data.get('description',      p.get('description', '')).strip()
    return jsonify({"message": f"商品 ID={pid} 已更新", "product": p})


# DELETE /products/<id>   刪除商品
@app.route('/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    p = find_product(pid)
    if not p:
        return jsonify({"error": "找不到商品"}), 404
    products.remove(p)
    return jsonify({"message": f"商品『{p['name']}』已刪除"})


# ─────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)
