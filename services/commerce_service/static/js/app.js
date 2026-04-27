/* NovaMarket — frontend interactions */

(function () {
    "use strict";

    /* ─────────────────────────────────────────────
       CART — quantity controls
    ───────────────────────────────────────────── */
    function initCartQuantity() {
        document.querySelectorAll(".qty-control").forEach(function (ctrl) {
            var input = ctrl.querySelector(".qty-input");
            var decBtn = ctrl.querySelector(".qty-dec");
            var incBtn = ctrl.querySelector(".qty-inc");
            var form = ctrl.closest("form");
            if (!input) return;

            if (decBtn) {
                decBtn.addEventListener("click", function () {
                    var v = Math.max(1, parseInt(input.value, 10) - 1);
                    input.value = v;
                    if (form) form.submit();
                });
            }

            if (incBtn) {
                incBtn.addEventListener("click", function () {
                    input.value = parseInt(input.value, 10) + 1;
                    if (form) form.submit();
                });
            }
        });
    }

    /* ─────────────────────────────────────────────
       CHATBOT
    ───────────────────────────────────────────── */
    function initChatbot() {
        var fab = document.getElementById("chat-fab");
        var popup = document.getElementById("chat-popup");
        var closeBtn = document.getElementById("chat-close");
        var messagesEl = document.getElementById("chat-messages");
        var inputEl = document.getElementById("chat-input");
        var sendBtn = document.getElementById("chat-send");

        if (!fab || !popup) return;

        var isOpen = false;
        var sessionKey = getSessionKey();
        var thinking = false;

        function getSessionKey() {
            var key = sessionStorage.getItem("nova_session");
            if (!key) {
                key = "sess_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
                sessionStorage.setItem("nova_session", key);
            }
            return key;
        }

        function toggleChat() {
            isOpen = !isOpen;
            popup.classList.toggle("open", isOpen);
            fab.classList.toggle("open", isOpen);
            fab.setAttribute("aria-expanded", isOpen);
            if (isOpen) {
                setTimeout(function () { inputEl && inputEl.focus(); }, 220);
                scrollToBottom();
            }
        }

        function scrollToBottom() {
            if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
        }

        function appendMessage(role, html) {
            if (!messagesEl) return null;
            var div = document.createElement("div");
            div.className = "chat-msg chat-msg-" + role;
            var bubble = document.createElement("div");
            bubble.className = "chat-msg-bubble";
            bubble.innerHTML = html;
            div.appendChild(bubble);
            messagesEl.appendChild(div);
            scrollToBottom();
            return div;
        }

        function showTyping() {
            if (!messagesEl) return null;
            var div = document.createElement("div");
            div.className = "chat-msg chat-msg-bot";
            div.id = "chat-typing";
            div.innerHTML = '<div class="chat-typing"><span></span><span></span><span></span></div>';
            messagesEl.appendChild(div);
            scrollToBottom();
            return div;
        }

        function removeTyping() {
            var el = document.getElementById("chat-typing");
            if (el) el.remove();
        }

        function buildProductPills(products) {
            if (!products || products.length === 0) return "";
            var html = '<div class="chat-msg-products">';
            products.slice(0, 3).forEach(function (p) {
                var url = p.absolute_url || ("/products/" + p.slug + "/");
                html += '<a href="' + escapeHtml(url) + '" class="chat-product-pill">' +
                    '<span class="chat-product-pill-name">' + escapeHtml(p.name) + '</span>' +
                    '<span class="chat-product-pill-price">$' + escapeHtml(String(p.price)) + '</span>' +
                    '</a>';
            });
            html += "</div>";
            return html;
        }

        function buildSuggestedPrompts(prompts) {
            if (!prompts || prompts.length === 0) return "";
            var html = '<div class="chat-suggested">';
            prompts.slice(0, 3).forEach(function (p) {
                html += '<button class="chat-suggested-btn" type="button">' + escapeHtml(p) + '</button>';
            });
            html += "</div>";
            return html;
        }

        function escapeHtml(str) {
            return String(str)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;");
        }

        function sendMessage(text) {
            if (!text || thinking) return;
            text = text.trim();
            if (!text) return;

            appendMessage("user", escapeHtml(text));
            if (inputEl) inputEl.value = "";
            thinking = true;
            if (sendBtn) sendBtn.disabled = true;

            showTyping();

            var cartSlugs = [];
            document.querySelectorAll("[data-product-slug]").forEach(function (el) {
                cartSlugs.push(el.dataset.productSlug);
            });

            fetch("/api/ai/chat/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_key: sessionKey,
                    message: text,
                    source: "assistant",
                    context: {
                        query: text,
                        cart_product_slugs: cartSlugs,
                        cart_category_names: []
                    }
                })
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                removeTyping();
                var html = escapeHtml(data.answer || "Sorry, I couldn't get a response.");
                html += buildProductPills(data.recommended_products);
                html += buildSuggestedPrompts(data.suggested_prompts);
                var msgEl = appendMessage("bot", html);
                if (msgEl) {
                    msgEl.querySelectorAll(".chat-suggested-btn").forEach(function (btn) {
                        btn.addEventListener("click", function () { sendMessage(btn.textContent); });
                    });
                }
            })
            .catch(function () {
                removeTyping();
                appendMessage("bot", "I'm having trouble connecting right now. Please try again in a moment.");
            })
            .finally(function () {
                thinking = false;
                if (sendBtn) sendBtn.disabled = false;
                if (inputEl) inputEl.focus();
            });
        }

        fab.addEventListener("click", toggleChat);
        if (closeBtn) closeBtn.addEventListener("click", toggleChat);

        if (sendBtn) {
            sendBtn.addEventListener("click", function () {
                if (inputEl) sendMessage(inputEl.value);
            });
        }

        if (inputEl) {
            inputEl.addEventListener("keydown", function (e) {
                if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage(inputEl.value);
                }
            });
        }

        document.addEventListener("click", function (e) {
            if (isOpen && !popup.contains(e.target) && e.target !== fab && !fab.contains(e.target)) {
                toggleChat();
            }
        });

        var welcomeHtml =
            "Hi! I'm Nova, your AI shopping assistant. 👋 I can help you find products, " +
            "compare items, or answer questions about our catalog." +
            '<div class="chat-suggested">' +
            '<button class="chat-suggested-btn" type="button">What\'s popular?</button>' +
            '<button class="chat-suggested-btn" type="button">Help me find a gift</button>' +
            '<button class="chat-suggested-btn" type="button">Show wellness products</button>' +
            '</div>';

        var welcomeEl = appendMessage("bot", welcomeHtml);
        if (welcomeEl) {
            welcomeEl.querySelectorAll(".chat-suggested-btn").forEach(function (btn) {
                btn.addEventListener("click", function () { sendMessage(btn.textContent); });
            });
        }
    }

    /* ─────────────────────────────────────────────
       NAV active state
    ───────────────────────────────────────────── */
    function initActiveNav() {
        var path = window.location.pathname;
        document.querySelectorAll(".nav-link[data-path]").forEach(function (link) {
            var lp = link.dataset.path;
            if (lp === "/" && path === "/") {
                link.classList.add("active");
            } else if (lp !== "/" && path.startsWith(lp)) {
                link.classList.add("active");
            }
        });
    }

    /* ─────────────────────────────────────────────
       INIT
    ───────────────────────────────────────────── */
    document.addEventListener("DOMContentLoaded", function () {
        initActiveNav();
        initCartQuantity();
        initChatbot();
    });
})();
