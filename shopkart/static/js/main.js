// ── Cart ──────────────────────────────────────────────────────
function addToCart(productId, btn) {
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Adding...';
    btn.disabled = true;

    const formData = new FormData();
    formData.append('quantity', 1);

    fetch(`/cart/add/${productId}`, { method: 'POST', body: formData })
        .then(r => r.json())
        .then(data => {
            if (data.redirect) {
                window.location.href = data.redirect;
                return;
            }
            if (data.success) {
                // Update all cart badges
                document.querySelectorAll('#cart-badge').forEach(el => {
                    el.textContent = data.cart_count;
                });
                showToast('✅ Added to cart!');
                btn.innerHTML = '<i class="fas fa-check me-1"></i> Added!';
                btn.style.background = '#26a541';
                btn.style.color = 'white';
                btn.style.borderColor = '#26a541';
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.background = '';
                    btn.style.color = '';
                    btn.style.borderColor = '';
                    btn.disabled = false;
                }, 1800);
            }
        })
        .catch(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
            showToast('Something went wrong. Try again.');
        });
}

// ── Wishlist ───────────────────────────────────────────────────
function toggleWishlist(productId, btn) {
    fetch(`/wishlist/toggle/${productId}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.redirect) { window.location.href = data.redirect; return; }
            if (data.success) {
                const icon = btn.querySelector('i');
                if (data.added) {
                    btn.classList.add('active');
                    if (icon) { icon.classList.remove('far'); icon.classList.add('fas'); }
                    if (btn.tagName === 'BUTTON' && btn.classList.contains('btn-wishlist-lg')) {
                        btn.innerHTML = '<i class="fas fa-heart me-2"></i>Wishlisted';
                        btn.classList.add('active');
                    }
                    showToast('❤️ Added to wishlist!');
                } else {
                    btn.classList.remove('active');
                    if (icon) { icon.classList.remove('fas'); icon.classList.add('far'); }
                    if (btn.tagName === 'BUTTON' && btn.classList.contains('btn-wishlist-lg')) {
                        btn.innerHTML = '<i class="far fa-heart me-2"></i>Wishlist';
                        btn.classList.remove('active');
                    }
                    showToast('💔 Removed from wishlist');
                }
            }
        })
        .catch(() => showToast('Something went wrong. Try again.'));
}

// ── Toast Notification ─────────────────────────────────────────
function showToast(message) {
    const toastEl = document.getElementById('cartToast');
    const msgEl = document.getElementById('toastMsg');
    if (!toastEl) return;
    if (msgEl) msgEl.textContent = message;
    const toast = new bootstrap.Toast(toastEl, { delay: 2500 });
    toast.show();
}

// ── Quantity Input Validation ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Animate product cards on load
    const cards = document.querySelectorAll('.product-card');
    cards.forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(16px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 50 + i * 40);
    });

    // Auto-dismiss alerts
    setTimeout(() => {
        document.querySelectorAll('.sk-alert').forEach(el => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
            if (bsAlert) bsAlert.close();
        });
    }, 4000);

    // Price filter: validate min < max
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', e => {
            const min = parseFloat(filterForm.querySelector('[name=min_price]')?.value) || 0;
            const max = parseFloat(filterForm.querySelector('[name=max_price]')?.value) || Infinity;
            if (min > max) {
                e.preventDefault();
                alert('Minimum price cannot exceed maximum price.');
            }
        });
    }

    // Smooth scroll to products section
    document.querySelectorAll('a[href="#products"]').forEach(a => {
        a.addEventListener('click', e => {
            e.preventDefault();
            document.getElementById('products')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });

    // Star picker interactive highlight for reviews
    document.querySelectorAll('.star-picker label').forEach(label => {
        label.addEventListener('mouseenter', () => {
            label.style.color = '#fb641b';
        });
        label.addEventListener('mouseleave', () => {
            label.style.color = '';
        });
    });

    // Sticky navbar shadow on scroll
    const navbar = document.querySelector('.main-navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 60) {
            navbar?.classList.add('scrolled');
        } else {
            navbar?.classList.remove('scrolled');
        }
    });
});
