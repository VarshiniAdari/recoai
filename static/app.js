// ============================================================
// RecoAI — App JS (Redesigned 2024)
// ============================================================

let allResults = [];

function fmt(n) {
    return '₹' + Number(n).toLocaleString('en-IN');
}
function fmtRev(n) {
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n;
}

// Budget labels
function updateBudgetLabels() {
    const min = document.getElementById('budgetMin').value;
    const max = document.getElementById('budgetMax').value;
    document.getElementById('sliderMinLabel').textContent = Number(min).toLocaleString('en-IN');
    document.getElementById('sliderMaxLabel').textContent = Number(max).toLocaleString('en-IN');
}
document.getElementById('budgetMin').addEventListener('input', updateBudgetLabels);
document.getElementById('budgetMax').addEventListener('input', updateBudgetLabels);
updateBudgetLabels();

// Quick feature tags
document.querySelectorAll('.qtag').forEach(btn => {
    btn.addEventListener('click', () => {
        const tag = btn.dataset.tag;
        const ta = document.getElementById('features');
        const curr = ta.value.trim();
        if (!curr.toLowerCase().includes(tag.toLowerCase())) {
            ta.value = curr ? curr + ', ' + tag : tag;
        }
    });
});

// Use-case buttons
let selectedUseCase = '';
document.querySelectorAll('.uc-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.uc-btn').forEach(b => b.classList.remove('active'));
        if (selectedUseCase === btn.dataset.value) {
            selectedUseCase = '';
            document.getElementById('useCase').value = '';
        } else {
            btn.classList.add('active');
            selectedUseCase = btn.dataset.value;
            document.getElementById('useCase').value = selectedUseCase;
        }
    });
});

// Advanced toggle
const advBtn = document.getElementById('advBtn');
const advContent = document.getElementById('advContent');
let advOpen = false;
advBtn.addEventListener('click', () => {
    advOpen = !advOpen;
    advContent.style.display = advOpen ? 'block' : 'none';
    advBtn.innerHTML = advOpen
        ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/></svg> Hide Options`
        : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg> Advanced Options`;
});

// Sort
document.getElementById('sortSelect').addEventListener('change', (e) => {
    if (!allResults.length) return;
    let sorted = [...allResults];
    switch (e.target.value) {
        case 'score': sorted.sort((a, b) => b.match_score - a.match_score); break;
        case 'price_asc': sorted.sort((a, b) => a.price - b.price); break;
        case 'price_desc': sorted.sort((a, b) => b.price - a.price); break;
        case 'rating': sorted.sort((a, b) => b.rating - a.rating); break;
    }
    renderProducts(sorted);
});

// Loading steps animation
let stepTimer = null;
function animateSteps() {
    clearTimeout(stepTimer);
    let i = 0;
    const nums = [1, 2, 3, 4, 5];
    [1,2,3,4,5].forEach(n => {
        const el = document.getElementById('step'+n);
        if (el) el.classList.remove('active', 'done');
    });
    function next() {
        if (i > 0) {
            const prev = document.getElementById('step' + nums[i - 1]);
            if (prev) prev.classList.replace('active', 'done');
        }
        if (i < nums.length) {
            const cur = document.getElementById('step' + nums[i]);
            if (cur) cur.classList.add('active');
            i++;
            stepTimer = setTimeout(next, 900);
        }
    }
    next();
}

// Show panels
function showPanel(name) {
    ['emptyState', 'loadingState', 'resultsContainer', 'errorState'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
    });
    const t = { empty: 'emptyState', loading: 'loadingState', results: 'resultsContainer', error: 'errorState' };
    const el = document.getElementById(t[name]);
    if (el) el.style.display = '';
}

// Score ring
function animateScoreRing(arcEl, score) {
    const circumference = 2 * Math.PI * 32;
    arcEl.style.strokeDasharray = circumference;
    const color = score >= 0.8 ? '#10b981' : score >= 0.6 ? '#2563eb' : score >= 0.4 ? '#f59e0b' : '#ef4444';
    arcEl.style.stroke = color;
    setTimeout(() => {
        arcEl.style.strokeDashoffset = circumference * (1 - score);
    }, 150);
}

// Build a product card
function buildCard(product, rank) {
    const tpl = document.getElementById('productCardTemplate');
    const card = tpl.content.cloneNode(true).querySelector('.pcard');

    if (rank === 1) card.classList.add('top-card');

    const rankEl = card.querySelector('.rank-badge');
    rankEl.textContent = '#' + rank;
    if (rank === 1) rankEl.classList.add('rank-1');

    card.querySelector('.pcard-brand').textContent = product.brand || 'Unknown';
    card.querySelector('.pcard-title').textContent = product.title;
    card.querySelector('.pcard-price').textContent = fmt(product.price);
    card.querySelector('.rv').textContent = product.rating;
    card.querySelector('.rc').textContent = '(' + fmtRev(product.num_reviews) + ')';

    const tier = product.performance_tier || 'mid-range';
    const tierEl = card.querySelector('.perf-tier');
    tierEl.textContent = tier.charAt(0).toUpperCase() + tier.slice(1);

    // Score ring
    const score = product.match_score;
    card.querySelector('.score-val').textContent = Math.round(score * 100) + '%';
    const arc = card.querySelector('.score-arc');
    setTimeout(() => animateScoreRing(arc, score), 100);

    // Features
    const featsCont = card.querySelector('.pcard-features');
    (product.key_features || []).slice(0, 5).forEach(f => {
        const chip = document.createElement('span');
        chip.className = 'feat-chip';
        chip.textContent = f;
        featsCont.appendChild(chip);
    });

    // Pros
    const prosUl = card.querySelector('.pros-ul');
    (product.pros || []).slice(0, 3).forEach(p => {
        const li = document.createElement('li');
        li.textContent = p;
        prosUl.appendChild(li);
    });

    // Cons
    const consUl = card.querySelector('.cons-ul');
    (product.cons || []).slice(0, 3).forEach(c => {
        const li = document.createElement('li');
        li.textContent = c;
        consUl.appendChild(li);
    });

    // Score bars
    const bd = product.score_breakdown || {};
    function setBar(fillCls, valCls, val, max) {
        const pct = Math.round((val / max) * 100);
        setTimeout(() => {
            const fill = card.querySelector('.' + fillCls);
            if (fill) fill.style.width = pct + '%';
        }, 350);
        const valEl = card.querySelector('.' + valCls);
        if (valEl) valEl.textContent = Math.round(val);
    }
    setBar('bf-budget', 'bv-budget', bd.budget || 0, 30);
    setBar('bf-feat', 'bv-feat', bd.features || 0, 25);
    setBar('bf-uc', 'bv-uc', bd.use_case || 0, 20);
    setBar('bf-qual', 'bv-qual', bd.quality || 0, 15);

    // Explanation
    const explToggle = card.querySelector('.expl-toggle');
    const explBody = card.querySelector('.expl-body');
    const explChev = card.querySelector('.expl-chevron');
    card.querySelector('.expl-text').textContent = product.explanation || 'Generating explanation...';
    explToggle.addEventListener('click', () => {
        const open = explBody.style.display === 'none' || !explBody.style.display;
        explBody.style.display = open ? 'block' : 'none';
        explChev.classList.toggle('open', open);
    });

    // Seller & link
    card.querySelector('.seller-nm').textContent = product.seller || 'Online Seller';
    card.querySelector('.pcard-view-btn').href = product.product_url || '#';

    return card;
}

function renderProducts(products) {
    const list = document.getElementById('productsList');
    list.innerHTML = '';
    products.forEach((p, i) => {
        list.appendChild(buildCard(p, i + 1));
    });
}

// Form submit
document.getElementById('preferenceForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const budgetMin = document.getElementById('budgetMin').value || 0;
    const budgetMax = document.getElementById('budgetMax').value || 999999;
    const productType = document.getElementById('productType').value;
    const features = document.getElementById('features').value;
    const useCase = document.getElementById('useCase').value;
    const brandPref = document.getElementById('brandPref') ? document.getElementById('brandPref').value : '';
    const avoidBrands = document.getElementById('avoidBrands') ? document.getElementById('avoidBrands').value : '';
    const topN = document.getElementById('topN').value;

    if (!productType) {
        const sel = document.getElementById('productType');
        sel.style.borderColor = '#ef4444';
        sel.focus();
        setTimeout(() => sel.style.borderColor = '', 2500);
        return;
    }

    showPanel('loading');
    animateSteps();

    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    submitBtn.disabled = true;
    btnText.textContent = 'Analyzing...';

    try {
        const resp = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                budget_min: parseFloat(budgetMin),
                budget_max: parseFloat(budgetMax),
                product_type: productType,
                features, use_case: useCase,
                brand_preference: brandPref,
                avoid_brands: avoidBrands,
                top_n: parseInt(topN)
            })
        });

        const data = await resp.json();
        if (!resp.ok || data.error) throw new Error(data.error || 'Request failed');

        allResults = data.recommendations || [];

        document.getElementById('resultsTitle').textContent = `Top ${allResults.length} Recommendations`;
        document.getElementById('resultsSubtitle').textContent =
            `Best matches for ${productType} · Budget: ${fmt(budgetMin)} – ${fmt(budgetMax)}${useCase ? ' · ' + useCase : ''}`;

        const best = allResults[0];
        if (best) {
            document.getElementById('resultsSummary').innerHTML =
                `🎯 Best match: <strong>${best.title}</strong> — <strong>${Math.round(best.match_score * 100)}% match</strong> at ${fmt(best.price)}`;
        }

        renderProducts(allResults);
        showPanel('results');

    } catch (err) {
        document.getElementById('errorMessage').textContent = err.message || 'Unknown error';
        showPanel('error');
    } finally {
        submitBtn.disabled = false;
        btnText.textContent = 'Find Best Products';
        clearTimeout(stepTimer);
    }
});
