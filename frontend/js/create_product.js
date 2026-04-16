document.getElementById('productForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorMsg = document.getElementById('errorMsg');
      const submitBtn = document.getElementById('submitBtn');
      errorMsg.classList.add('hidden');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Creando...';

      const body = {
        name: document.getElementById('name').value,
        unit: document.getElementById('unit').value,
        purchase_price: parseFloat(document.getElementById('purchase_price').value),
        sale_price: parseFloat(document.getElementById('sale_price').value),
        stock: parseInt(document.getElementById('stock').value),
      };

      try {
        const res = await apiFetch('/products/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });

        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || 'Error al crear el producto');
        }

        window.location.href = 'index.html';

      } catch (err) {
        errorMsg.textContent = err.message;
        errorMsg.classList.remove('hidden');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Crear producto';
      }
    });