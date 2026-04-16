const params = new URLSearchParams(window.location.search);
    const productId = params.get('id');
    if (!productId) window.location.href = 'index.html';

    document.getElementById('backBtn').href = `product.html?id=${productId}`;

    // Cargar datos actuales del producto
    async function loadProduct() {
      try {
        const res = await apiFetch(`/products/${productId}`);
        if (!res.ok) throw new Error('Producto no encontrado');
        const p = await res.json();

        document.getElementById('name').value = p.name;
        document.getElementById('unit').value = p.unit;
        document.getElementById('purchase_price').value = p.purchase_price;
        document.getElementById('sale_price').value = p.sale_price;

      } catch (err) {
        const errorMsg = document.getElementById('errorMsg');
        errorMsg.textContent = err.message;
        errorMsg.classList.remove('hidden');
      }
    }

    document.getElementById('editForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorMsg = document.getElementById('errorMsg');
      const submitBtn = document.getElementById('submitBtn');
      errorMsg.classList.add('hidden');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Guardando...';

      // Solo manda los campos que tienen valor
      const body = {};
      const name = document.getElementById('name').value;
      const unit = document.getElementById('unit').value;
      const purchase_price = document.getElementById('purchase_price').value;
      const sale_price = document.getElementById('sale_price').value;

      if (name) body.name = name;
      if (unit) body.unit = unit;
      if (purchase_price) body.purchase_price = parseFloat(purchase_price);
      if (sale_price) body.sale_price = parseFloat(sale_price);

      try {
        const res = await apiFetch(`/products/${productId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });

        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || 'Error al actualizar el producto');
        }

        window.location.href = `product.html?id=${productId}`;

      } catch (err) {
        errorMsg.textContent = err.message;
        errorMsg.classList.remove('hidden');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Guardar cambios';
      }
    });

    loadProduct();