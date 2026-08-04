const initialPapers = [
  { id: 1, title: 'DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning', venue: 'arXiv · 2025', year: 2025, status: 'reading', tags: ['LLM', 'Reasoning'], summary: '通过纯强化学习激励大语言模型的推理能力，展示了无需人工标注推理轨迹也可以涌现出强大的长链思考能力。', innovations: ['提出 GRPO 算法，在不依赖 critic model 的情况下优化策略。', '观察并分析了模型自发涌现的自我验证与反思行为。', '通过多阶段训练，将推理能力有效迁移到通用任务。'], notes: '推理时的 token budget 和训练时的奖励设计值得深入对比。可以关注它与 process reward model 的结合方式。', updated: '今天 10:24', date: '2026-08-04' },
  { id: 2, title: 'Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection', venue: 'ICLR · 2024', year: 2024, status: 'read', tags: ['RAG', 'Evaluation'], summary: 'Self-RAG 让语言模型学习何时检索、检索什么以及如何评价自己的生成结果，在准确性和事实性之间取得更好的平衡。', innovations: ['引入 reflection tokens 统一控制检索与自我批评。', '训练模型根据检索结果对生成内容进行自我评价。'], notes: 'Reflection token 是很有价值的接口设计。后续可以迁移到多轮 Agent 的工具调用决策。', updated: '昨天 16:40', date: '2026-08-03' },
  { id: 3, title: 'The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits', venue: 'arXiv · 2024', year: 2024, status: 'later', tags: ['LLM', 'Efficiency'], summary: '探索将大语言模型权重压缩到三值 {−1, 0, +1}，在显著降低内存与计算成本的同时保持模型能力。', innovations: ['提出 1.58-bit 权重表示，让矩阵乘法可以用加法替代。', '讨论了从预训练阶段开始使用三值权重的可行性。'], notes: '需要结合实际硬件 benchmark 判断收益。', updated: '3 天前', date: '2026-08-01' },
  { id: 4, title: 'SWE-bench: Can Language Models Resolve Real-World GitHub Issues?', venue: 'ICLR · 2024', year: 2024, status: 'reading', tags: ['Agent', 'Evaluation'], summary: '一个评估语言模型解决真实 GitHub issue 能力的基准测试，任务包含理解代码库、定位问题与生成可合并的补丁。', innovations: ['使用真实开源项目 issue，避免了合成任务的评估偏差。', '建立可执行测试驱动的端到端评估流程。'], notes: '评测结果高度依赖上下文构造方式，适合作为 Agent 系统的回归测试集。', updated: '上周五', date: '2026-07-31' }
];

const statusText = { reading: '正在阅读', read: '已读', later: '稍后阅读' };
let papers = loadPapers();
let activeFilter = 'all';
let activeTag = null;
let selectedId = papers[0]?.id ?? null;
let sortNewest = true;
let editingId = null;

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function loadPapers() {
  try { return JSON.parse(localStorage.getItem('paperbase-papers')) || initialPapers; } catch { return initialPapers; }
}
function persist() { localStorage.setItem('paperbase-papers', JSON.stringify(papers)); }
function escapeHtml(value = '') { return String(value).replace(/[&<>'"]/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#039;', '"':'&quot;' }[char])); }
function getFilteredPapers() {
  const query = $('#searchInput').value.trim().toLowerCase();
  let result = papers.filter(p => activeFilter === 'all' || p.status === activeFilter);
  if (activeTag) result = result.filter(p => p.tags.some(tag => tag.toLowerCase() === activeTag.toLowerCase()));
  if (query) result = result.filter(p => [p.title, p.venue, p.summary, p.notes, ...p.tags].join(' ').toLowerCase().includes(query));
  return result.sort((a, b) => sortNewest ? b.id - a.id : a.id - b.id);
}
function render() {
  const filtered = getFilteredPapers();
  $('#paperList').innerHTML = filtered.map(p => `<article class="paper-card ${p.id === selectedId ? 'selected' : ''}" data-id="${p.id}">
    <div class="card-top"><span class="card-status status-${p.status}">${statusText[p.status]}</span><span class="card-year">${escapeHtml(p.year || '')}</span></div>
    <h3>${escapeHtml(p.title)}</h3><p>${escapeHtml(p.venue)} · ${escapeHtml(p.summary)}</p>
    <div class="card-bottom">${p.tags.slice(0, 3).map(tag => `<span class="mini-tag">${escapeHtml(tag)}</span>`).join('')}</div>
  </article>`).join('');
  $('#emptyState').hidden = filtered.length !== 0;
  $('#libraryCount').textContent = papers.length;
  $('#allCount').textContent = papers.length;
  $('#readingCount').textContent = papers.filter(p => p.status === 'reading').length;
  $('#readCount').textContent = papers.filter(p => p.status === 'read').length;
  $('#laterCount').textContent = papers.filter(p => p.status === 'later').length;
  $$('.paper-card').forEach(card => card.addEventListener('click', () => { selectedId = Number(card.dataset.id); render(); }));
  renderDetail();
}
function renderDetail() {
  const paper = papers.find(p => p.id === selectedId);
  if (!paper) { $('#detailEmpty').hidden = false; $('#detailContent').hidden = true; return; }
  $('#detailEmpty').hidden = true; $('#detailContent').hidden = false;
  $('#detailStatus').textContent = statusText[paper.status];
  $('#detailStatus').className = `status-pill status-${paper.status}`;
  $('#detailUpdated').textContent = paper.updated || '刚刚更新';
  $('#detailTitle').textContent = paper.title;
  $('#detailVenue').textContent = `${paper.venue}  ·  ${paper.year || '未标注年份'}`;
  $('#detailTags').innerHTML = paper.tags.map(tag => `<span class="mini-tag">${escapeHtml(tag)}</span>`).join('');
  $('#detailSummary').textContent = paper.summary || '还没有添加概要。';
  $('#detailInnovations').innerHTML = (paper.innovations || []).filter(Boolean).map(item => `<p>${escapeHtml(item)}</p>`).join('') || '<p>还没有添加创新点。</p>';
  $('#detailNotes').textContent = paper.notes || '还没有添加笔记。';
  $('#detailDate').textContent = `最后编辑于 ${paper.date || '今天'}`;
  const progress = paper.status === 'read' ? 100 : paper.status === 'reading' ? 57 : 0;
  $('#progressBar').style.width = `${progress}%`;
  $('#progressLabel').textContent = paper.status === 'read' ? '已完成阅读' : paper.status === 'reading' ? '正在形成初步理解' : '加入阅读队列';
}
function openModal(paper = null) {
  editingId = paper?.id ?? null;
  $('#modalTitle').textContent = paper ? '编辑论文' : '新建论文';
  const form = $('#paperForm'); form.reset();
  if (paper) Object.entries({ title: paper.title, venue: paper.venue, year: paper.year, status: paper.status, tags: paper.tags.join(', '), summary: paper.summary, innovations: paper.innovations.join('\n'), notes: paper.notes }).forEach(([key, value]) => { form.elements[key].value = value ?? ''; });
  $('#modalBackdrop').hidden = false;
  setTimeout(() => form.elements.title.focus(), 30);
}
function closeModal() { $('#modalBackdrop').hidden = true; editingId = null; }
function showToast(message) { const toast = $('#toast'); toast.textContent = message; toast.classList.add('show'); setTimeout(() => toast.classList.remove('show'), 2200); }

$$('.nav-item').forEach(button => button.addEventListener('click', () => { activeFilter = button.dataset.filter; activeTag = null; $$('.nav-item').forEach(item => item.classList.toggle('active', item === button)); $$('.tag-filter').forEach(item => item.classList.remove('active')); $('#viewTitle').textContent = button.querySelector('span:not(.nav-icon)').textContent; render(); }));
$$('.tag-filter').forEach(button => button.addEventListener('click', () => { activeTag = button.dataset.tag; activeFilter = 'all'; $$('.nav-item').forEach(item => item.classList.toggle('active', item.dataset.filter === 'all')); $$('.tag-filter').forEach(item => item.classList.toggle('active', item === button)); $('#viewTitle').textContent = button.textContent.trim(); render(); }));
$('#searchInput').addEventListener('input', render);
$('#sortBtn').addEventListener('click', () => { sortNewest = !sortNewest; $('#sortBtn').firstChild.textContent = sortNewest ? '最近更新 ' : '最早更新 '; render(); });
$('#newPaperBtn').addEventListener('click', () => openModal());
$('#editBtn').addEventListener('click', () => { const paper = papers.find(p => p.id === selectedId); if (paper) openModal(paper); });
$('#deleteBtn').addEventListener('click', () => { const paper = papers.find(p => p.id === selectedId); if (!paper || !confirm(`确定删除《${paper.title}》吗？`)) return; papers = papers.filter(p => p.id !== selectedId); selectedId = papers[0]?.id ?? null; persist(); render(); showToast('论文已删除'); });
$('#duplicateBtn').addEventListener('click', () => { const paper = papers.find(p => p.id === selectedId); if (!paper) return; const copy = { ...paper, id: Date.now(), title: `${paper.title}（副本）`, status: 'later', updated: '刚刚更新', date: new Date().toISOString().slice(0, 10) }; papers.unshift(copy); selectedId = copy.id; persist(); render(); showToast('已复制一份论文记录'); });
$('#paperForm').addEventListener('submit', event => { event.preventDefault(); const data = new FormData(event.currentTarget); const entry = { title: data.get('title').trim(), venue: data.get('venue').trim(), year: Number(data.get('year')) || new Date().getFullYear(), status: data.get('status'), tags: data.get('tags').split(/[,，]/).map(item => item.trim()).filter(Boolean), summary: data.get('summary').trim(), innovations: data.get('innovations').split('\n').map(item => item.trim()).filter(Boolean), notes: data.get('notes').trim(), updated: '刚刚更新', date: new Date().toISOString().slice(0, 10) }; if (editingId) { papers = papers.map(p => p.id === editingId ? { ...p, ...entry } : p); selectedId = editingId; showToast('论文已更新'); } else { entry.id = Date.now(); papers.unshift(entry); selectedId = entry.id; showToast('论文已添加到论文库'); } persist(); closeModal(); render(); });
$('#closeModal').addEventListener('click', closeModal); $('#cancelModal').addEventListener('click', closeModal); $('#modalBackdrop').addEventListener('click', event => { if (event.target === $('#modalBackdrop')) closeModal(); });
document.addEventListener('keydown', event => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); $('#searchInput').focus(); } if (event.key === 'Escape' && !$('#modalBackdrop').hidden) closeModal(); });
render();
