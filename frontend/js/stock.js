 // Cargar productos en el select
    async function loadProducts() {
      try {
        const res = await apiFetch('/products/');
        const products = await res.json();

        const select = document.getElementById('productSelect');
        products.forEach(p => {
          const option = document.createElement('option');
          option.value = p.id;
          option.textContent = `${p.name} (stock: ${p.stock})`;
          option.dataset.name = p.name;
          option.dataset.stock = p.stock;
          select.appendChild(option);
        });
      } catch {
        // silencioso, el submit va a fallar igual
      }
    }

    // Mostrar info del producto seleccionado
    document.getElementById('productSelect').addEventListener('change', (e) => {
      const option = e.target.selectedOptions[0];
      const info = document.getElementById('productInfo');
      if (option.value) {
        document.getElementById('productName').textContent = option.dataset.name;
        document.getElementById('productStock').textContent = option.dataset.stock;
        info.classList.remove('hidden');
      } else {
        info.classList.add('hidden');
      }
    });

    document.getElementById('stockForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorMsg = document.getElementById('errorMsg');
      const submitBtn = document.getElementById('submitBtn');
      errorMsg.classList.add('hidden');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Procesando...';

      const productId = document.getElementById('productSelect').value;
      const type = document.querySelector('input[name="type"]:checked').value;
      const cantidad = parseInt(document.getElementById('quantity').value);
      const quantity = type === 'retiro' ? -cantidad : cantidad;

      try {
        const res = await apiFetch(`/products/${productId}/stock`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ quantity }),
        });

        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || 'Error al mover el stock');
        }

        window.location.href = 'index.html';

      } catch (err) {
        errorMsg.textContent = err.message;
        errorMsg.classList.remove('hidden');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Confirmar movimiento';
      }
    });

    loadProducts();