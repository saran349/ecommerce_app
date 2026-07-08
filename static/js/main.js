// main.js — talks to the Flask REST API (/api/cart, /api/cart/<id>)
// to add, update, and remove cart items without a full page reload.

document.addEventListener("DOMContentLoaded", () => {
  bindAddToCartButtons();
  bindCartPageControls();
});

// ---------------------------------------------------------------
// Add to cart (from product grid or product detail page)
// ---------------------------------------------------------------
function bindAddToCartButtons() {
  document.querySelectorAll(".btn-add-cart").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const productId = btn.dataset.productId;
      const qtyInputId = btn.dataset.qtyInput;
      const quantity = qtyInputId ? parseInt(document.getElementById(qtyInputId).value, 10) : 1;

      try {
        const res = await fetch("/api/cart", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ product_id: productId, quantity }),
        });

        if (res.status === 401 || res.redirected) {
          window.location.href = "/login";
          return;
        }

        const data = await res.json();
        if (!res.ok) {
          alert(data.error || "Could not add item to cart.");
          return;
        }

        btn.textContent = "Added ✓";
        setTimeout(() => (btn.textContent = "Add to Cart"), 1200);
      } catch (err) {
        console.error("Add to cart failed:", err);
        alert("Something went wrong. Please try again.");
      }
    });
  });
}

// ---------------------------------------------------------------
// Cart page: update quantity / remove item via REST API (PUT/DELETE)
// ---------------------------------------------------------------
function bindCartPageControls() {
  document.querySelectorAll(".qty-input").forEach((input) => {
    input.addEventListener("change", async () => {
      const itemId = input.dataset.cartItemId;
      const quantity = parseInt(input.value, 10);

      const res = await fetch(`/api/cart/${itemId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quantity }),
      });

      if (res.ok) {
        window.location.reload(); // simplest way to refresh subtotal/total display
      } else {
        const data = await res.json();
        alert(data.error || "Could not update quantity.");
      }
    });
  });

  document.querySelectorAll(".btn-remove").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const itemId = btn.dataset.cartItemId;
      const res = await fetch(`/api/cart/${itemId}`, { method: "DELETE" });

      if (res.ok) {
        document.querySelector(`tr[data-cart-item-id="${itemId}"]`)?.remove();
        window.location.reload();
      } else {
        const data = await res.json();
        alert(data.error || "Could not remove item.");
      }
    });
  });
}
